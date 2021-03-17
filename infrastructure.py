from datetime import datetime
from typing import Union

import requests
from bson.json_util import dumps
from eve.io.mongo import Validator
from flask import current_app, jsonify
from pymongo import MongoClient
from requests import Response

from authentication import WaitressAuth, land_api_auth
from collection_schemas import MICROSERVICE_LOG, LOCAL_USERS, WAITRESS_LOG, ORDER_LOG
from constants import (
    DATE_HMS_FORMAT,
    SUPERVISOR_SERVICE_API_MENU_URL,
    MICROSERVICE_TYPE,
    ORDERS_API_URL,
    MS_LOGS_API_URL,
    ORDERS_LOGS_API_URL,
    WAITRESS_LOGS_API_URL,
    EXTERNAL_API_VISITOR_URL,
    CLIENT_FAKE_HALL_TABLE,
    DEPOSIT_TABLE_NUMBERS,
    ACTION_LOG_FAKE_RESTAURANT_ID
)
from settings import (
    MONGO_HOST,
    MONGO_USERNAME,
    MONGO_PASSWORD,
    MONGO_PORT,
    MONGO_DBNAME,
)


# region ACTION_LOG collection actions
def get_action_log_data(filter=None, projection=None):
    fields_dict = {key: True for key in projection} if projection else {}
    fields_dict.update({'_id': False})

    db_interface = MongoDBInterface('action_log')
    data = db_interface.get_single_document(
        filter=filter if filter else {},
        projection=fields_dict,
        sort=[('$natural', -1)]
    )
    db_interface.close_connection()

    return data


def close_conductor_session():
    db_interface = MongoDBInterface('action_log')
    db_interface.update_single_document(
        {'waitress_status': {'$ne': 'C'}},
        {'$set': {'waitress_status': 'C', 'session_datetime_close': datetime.now().strftime(DATE_HMS_FORMAT)}}
    )
    log_client = LogManager(request=None)
    log_client.save_waitress_log(status='C', cancel_source='T')

    db_interface = MongoDBInterface('orders')

    for order in db_interface.get_all_documents({'status': 'O'}, {'_id': True}):
        log_client.save_order_log(
            status='C',
            cancel_source='S',
            hall=order['hall'],
            table=order['table'],
            order_details=db_interface.get_all_documents(
                filter={'_id': order['_id']}, projection={'_id': False, 'order_details': True}
            )[0]['order_details']
        )

        db_interface.update_single_document(
            {'_id': order['_id']},
            {'$set': {'status': 'C',
                      'cancel_source': 'S',
                      'datetime_close': datetime.now().strftime(DATE_HMS_FORMAT)}
             }
        )
        db_interface.close_connection()

        db_interface = MongoDBInterface('local_users')
        collection = db_interface.get_collection()
        collection.delete_many({'is_tablet': {'$ne': True}})

# endregion


class ClientManager:
    attrs = (
        ('mac', None),
        ('hall', None),
        ('table', None),
        ('lang', 'ru'),
        ('is_service_auth', False),
        ('is_deposit', False),
        ('current_deposit', 0)
    )

    def __init__(self, request, is_waitress):
        self.ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)
        self.is_waitress = is_waitress
        self.__authenticated = self._check_auth(request)
        data = self._global_client_search()
        for attr in self.attrs:
            setattr(self, attr[0], data.get(attr[0], attr[1]))
        self._fill_extra_properties()

    def get_client_data(self):
        return self._data()

    def get_client_data_response(self):
        data = self._data()
        data.update({'request_hall_table': True if self.need_request_hall_table else False})
        return jsonify(data)

    def insert_local_visitor_data(self, insertion_data=None):
        if insertion_data is not None:
            self._update_properties(insertion_data)

        data = self._data()

        v = Validator(LOCAL_USERS)
        if not v.validate(data):
            # print(v.errors)
            return False

        collection = current_app.data.driver.db['local_users']
        collection.find_one_and_update(
            {'ip': self.ip, 'is_waitress': self.is_waitress}, {'$set': data}, upsert=True
        )
        return True

    @property
    def is_authenticated(self):
        return self.__authenticated

    @property
    def need_request_hall_table(self):
        return any([
            None in (self.hall, self.table),
            (self.hall, self.table) == CLIENT_FAKE_HALL_TABLE
        ]) and not self.is_waitress

    @property
    def true_waitress(self):
        return all([self.is_waitress, self.is_authenticated])

    @property
    def true_visitor(self):
        return not any(
            [
                self.is_waitress,
                self.is_authenticated,
                None in (self.hall, self.table),
                (self.hall, self.table) == CLIENT_FAKE_HALL_TABLE
            ]
        )

    def _check_auth(self, request):
        auth_interface = WaitressAuth()
        auth_header = request.authorization
        return True if (auth_header and auth_interface.check_auth(
                auth_header.username, auth_header.password, None, None, None
        )) else False

    def _fill_extra_properties(self):
        # TODO Deposit for restoraunt
        self.is_deposit = True if self.hall in DEPOSIT_TABLE_NUMBERS else False

        if self.is_waitress:
            self.mac = self._get_external_api_visitor_data().get('mac', None)

        if (self.hall, self.table) == CLIENT_FAKE_HALL_TABLE:
            self.is_service_auth = True

    def _update_properties(self, insertion_data: dict) -> None:
        for key, val in insertion_data.items():
            setattr(self, key, val)
        self._fill_extra_properties()

    def _global_client_search(self):
        return self._get_local_visitor_data() or self._get_external_api_visitor_data()

    def _get_local_visitor_data(self):
        collection = current_app.data.driver.db['local_users']
        return collection.find_one(
            {'ip': self.ip, 'is_waitress': self.is_waitress},
            {'_id': False},
        )

    def _get_external_api_visitor_data(self):
        return requests.get(
            f'{EXTERNAL_API_VISITOR_URL}{self.ip.replace(".", "-")}'
        ).json()

    def _data(self):
        data = self.__dict__.copy()
        if '_ClientManager__authenticated' in data:
            data.pop('_ClientManager__authenticated')
        return data


class ClientRouter:
    def __init__(self, request):
        waitress = ClientManager(request, is_waitress=True)
        client = ClientManager(request, is_waitress=False)
        self.client = waitress if waitress.true_waitress else client


class MongoDBInterface:
    def __init__(self, collection_name):
        self.__client = MongoClient(self._get_uri())
        db = self.__client[MONGO_DBNAME]
        self.__collection = db[collection_name]

    def get_single_document(self, **kwargs) -> dict:
        return self.__collection.find_one(**kwargs)

    def get_all_documents(self, filter: dict, projection: dict) -> list:
        filter = filter if filter else {}
        projection = projection if filter else None
        return [*self.__collection.find(filter, projection)]

    def update_single_document(self, filter: dict, update: dict) -> dict:
        return self.__collection.find_one_and_update(filter, update)

    def update_all_documents(self, filter: dict, update: dict) -> dict:
        return self.__collection.update(filter, update, multi=True, upsert=True)

    def get_single_document_field(self, field: str, **kwargs) -> Union[str, bool]:
        document = self.__collection.find_one(**kwargs)
        return document.get(field, False) if document else False

    def insert_multiple(self, data: list):
        self.__collection.insert_many(data)
        self.close_connection()
    
    def insert_single(self, data: dict):
        self.__collection.insert_one(data)
        self.close_connection()

    def clean_data(self):
        self.__collection.remove()

    def get_collection(self):
        return self.__collection

    def _get_uri(self) -> str:
        return (f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DBNAME}'
                if MONGO_USERNAME and MONGO_HOST else f'mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DBNAME}')

    def close_connection(self):
        self.__client.close()


class LandAPIInterface:
    def pull_menu(self) -> None:
        if get_action_log_data({'waitress_status': 'S'}) or get_action_log_data({'waitress_status': 'P'}):
            return

        food_json = self._get_from_land_api_data(SUPERVISOR_SERVICE_API_MENU_URL, 'M')
        land_hash = food_json.get('hash', False) if food_json else False
        ms_hash = self._get_ms_last_modified()

        if not land_hash or (ms_hash == land_hash):
            return

        menu_json = food_json.get('results', False)
        if not menu_json:
            return

        db_interface = MongoDBInterface('food_category')
        db_interface.clean_data()

        # TODO Mix 'in_stock' field in land API serializer
        for category in menu_json:
            for food in category['foods']:
                food['in_stock'] = True

        db_interface.insert_multiple(menu_json)
        db_interface.close_connection()

        self._update_last_modified(land_hash)

    def push_orders(self) -> None:
        if get_action_log_data({'waitress_status': {'$ne': 'C'}}):
            return

        db_interface = MongoDBInterface('orders')
        orders = db_interface.get_all_documents(
            {'status': {'$ne': 'O'}},
            {'_id': False,
             '_created': False,
             '_updated': False,
             '_etag': False,
             'by_cash': False,
             'cash_nominal': False}
        )

        if not orders:
            return

        post_response = self._post_to_land_api_data(ORDERS_API_URL, orders, 'O')
        if post_response:
            db_interface.clean_data()
            db_interface.close_connection()

    def push_microservice_logs(self):
        self._push_any_logs('microservice_logs', MS_LOGS_API_URL)

    def push_order_logs(self):
        self._push_any_logs('order_logs', ORDERS_LOGS_API_URL)

    def push_waitress_log(self):
        self._push_any_logs('WAITRESS_LOGs', WAITRESS_LOGS_API_URL)

    def _push_any_logs(self, collection_name: str, api_url: str) -> None:
        db_interface = MongoDBInterface(collection_name)
        log_data = db_interface.get_all_documents(
            {},
            {'_id': False, '_created': False, '_updated': False, '_etag': False}
        )
        if not log_data:
            return

        post_response = self._post_to_land_api_data(api_url, log_data, 'L')
        if post_response:
            db_interface.clean_data()
            db_interface.close_connection()

        # TODO Save L-type logs after removing
        # if collection_name == 'microservice_logs':
        #     log_data = self._generate_ms_log('L', post_response)
        #     if self._validate_document(MICROSERVICE_LOG, log_data):
        #         self._save_microservice_logs('microservice_logs', log_data)

    def _save_microservice_logs(self, collection: str, data: dict) -> None:
        db_interface = MongoDBInterface(collection)
        db_interface.insert_single(data)
        db_interface.close_connection()

    def _update_last_modified(self, last_modified: int) -> None:
        # TODO with find_one_and_update
        db_interface = MongoDBInterface('bistro_last_modified')
        db_interface.clean_data()
        db_interface.insert_single({'bistro_last_modified': last_modified})
        db_interface.close_connection()

    def _get_ms_last_modified(self) -> Union[str, bool]:
        db_interface = MongoDBInterface('bistro_last_modified')
        data = db_interface.get_single_document_field('bistro_last_modified')
        db_interface.close_connection()
        return data

    def _generate_ms_log(self, log_action_tag: str, response: Union[Response, bool]) -> dict:
        restaurant_id = get_action_log_data({}, 'restaurant_id').values() if get_action_log_data() else ACTION_LOG_FAKE_RESTAURANT_ID
        return {
            'action_datetime': datetime.now().strftime(DATE_HMS_FORMAT),
            'request': log_action_tag,
            'response_code': response.status_code if response.status_code else None,
            'microservice_type': MICROSERVICE_TYPE,
            'restaurant_id': restaurant_id,
            'response': response.json() if response else {}
        }

    def _validate_document(self, data_schema: dict, document: dict) -> bool:
        v = Validator(data_schema)
        result = v.validate(document)
        # TODO collect validation errors
        # if not result:
        #     print(v.errors)

        return result

    def _get_from_land_api_data(self, url: str, log_action_tag: str) -> Union[dict, bool]:
        response = requests.get(url, auth=land_api_auth()) or False

        log_data = self._generate_ms_log(log_action_tag, response)
        if self._validate_document(MICROSERVICE_LOG, log_data):
            self._save_microservice_logs('microservice_logs', log_data)

        if not response or response.status_code != 200:
            return False

        return response.json()

    def _post_to_land_api_data(self, url: str, post_data: list, log_action_tag: str) -> bool:
        response = requests.post(
            headers={'Content-type': 'application/json'},
            url=url,
            auth=land_api_auth(),
            data=dumps(post_data),
        )
        log_data = self._generate_ms_log(log_action_tag, response)
        if self._validate_document(MICROSERVICE_LOG, log_data):
            self._save_microservice_logs('microservice_logs', log_data)

        return True if (response and response.status_code == 201) else False


class LogManager:
    def __init__(self, request=None):
        self.microservice_type = MICROSERVICE_TYPE
        self.action_datetime = datetime.now().strftime(DATE_HMS_FORMAT)
        for key, val in self._get_restaurant_data().items():
            setattr(self, key, val)

        if request:
            self.__client = ClientRouter(request).client
            for key, val in self._get_client_data(self.__client).items():
                setattr(self, key, val)
        else:
            self.ip = '127.0.0.1'
            self.mac = None

    def save_waitress_log(self, status: str, restaurant_id=None, cancel_source=None):
        log_data = self._get_log_base_data()
        log_data.update({'status': status, 'cancel_source': cancel_source})

        if restaurant_id:
            log_data.update({'restaurant_id': restaurant_id})

        self._insert_log_data('WAITRESS_LOGs', WAITRESS_LOG, log_data)

    def save_order_log(self, **kwargs):
        log_data = self._get_log_base_data()
        log_data.update(**kwargs)

        if 'hall' not in log_data:
            visitor_data = self._get_visitor_data(self.__client)
            log_data.update(visitor_data)

        self._insert_log_data('order_logs', ORDER_LOG, log_data)

    def _get_client_data(self, client: ClientManager):
        return {key: val for key, val in client.get_client_data().items() if key in ('ip', 'mac')}

    def _get_visitor_data(self, client: ClientManager):
        return {
            key: val for key, val in client.get_client_data().items() if key in ('hall', 'table')
        } if not client.is_waitress else {'hall': 1, 'table': 99}

    def _get_restaurant_data(self):
        return get_action_log_data({}, 'restaurant_id') or {'restaurant_id': None}

    def _get_log_base_data(self):
        data = self.__dict__.copy()
        if '_LogManager__client' in data:
            data.pop('_LogManager__client')
        return data

    def _insert_log_data(self, collection: str, schema: dict, insertion_data: dict):
        if not self._validate(schema, insertion_data):
            return

        db_interface = MongoDBInterface(collection)
        db_interface.insert_single(insertion_data)

    def _validate(self, schema: dict, insertion_data: dict):
        v = Validator(schema)
        # if not v.validate(insertion_data):
        #     print(v.errors)
        return v.validate(insertion_data)
