from datetime import datetime
from http import HTTPStatus

from eve.io.mongo import Validator
from flask import request, abort, current_app

from authentication import WaitressAuth
from collection_schemas import ORDER
from constants import DATE_HMS_FORMAT
from infrastructure import get_action_log_data, ClientManager, MongoDBInterface, LogManager


def open_waitress_session_actions(items):
    for item in items:
        item['session_datetime_open'] = datetime.now().strftime(DATE_HMS_FORMAT)

    restaurant_id = items[-1]['restaurant_id']

    client = ClientManager(request, is_waitress=True)
    client.insert_local_visitor_data()

    log_client = LogManager(request)
    log_client.save_waitress_log(status='S', restaurant_id=restaurant_id)

    collection = current_app.data.driver.db['action_log']
    collection.delete_many({'waitress_status': 'C', 'restaurant_id': {'$ne': restaurant_id}})


def change_waitress_session_actions(updates, original):
    log_client = LogManager(request)

    if updates['waitress_status'] in ['P', 'S']:
        log_client.save_waitress_log(status=updates['waitress_status'])

    if updates['waitress_status'] == 'C':
        log_client.save_waitress_log(status='С', cancel_source='M')
        updates['session_datetime_close'] = datetime.now().strftime(DATE_HMS_FORMAT)

        db_interface = MongoDBInterface('orders')
        for order in db_interface.get_all_documents({'status': 'O'}, {'_id': True, 'hall': True, 'table': True}):
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


def new_order_actions(items):
    waitress = ClientManager(request, is_waitress=True)
    visitor = ClientManager(request, is_waitress=False)

    if not waitress.true_waitress and not visitor.true_visitor:
        abort(HTTPStatus.FORBIDDEN, 'No visitor data was provided')

    action_log_data = get_action_log_data({'waitress_status': 'S'}, 'restaurant_id')
    if not action_log_data:
        abort(HTTPStatus.FORBIDDEN, 'Waitress is closed or suspended')

    client = waitress if waitress.true_waitress else visitor
    data = {
        key: val for key, val in client.get_client_data().items() if key in ('ip', 'mac', 'hall', 'table', 'lang')
    }
    data.update(action_log_data)
    data.update({'status': 'O', 'datetime_open': datetime.now().strftime(DATE_HMS_FORMAT)})

    schema = ORDER.copy()
    schema.pop('by_cash')
    v = Validator(schema)

    [order.update(data) for order in items if v.validate(data)]

    log_client = LogManager(request)
    log_client.save_order_log(status='O', cancel_source=None, order_details=items)


def close_order_actions(updates, original):
    waitress = ClientManager(request, is_waitress=True)
    visitor = ClientManager(request, is_waitress=False)

    if not waitress.true_waitress and not visitor.true_visitor:
        return

    cancel_source = 'C' if waitress.true_waitress else 'P'
    if updates['status'] in ['D', 'C']:
        updates['datetime_close'] = datetime.now().strftime(DATE_HMS_FORMAT)
        updates['cancel_source'] = cancel_source if updates['status'] == 'C' else None

    log_client = LogManager(request)
    log_client.save_order_log(
        status=updates['status'],
        hall=original['hall'],
        table=original['table'],
        cancel_source=cancel_source if updates['status'] == 'C' else None,
        order_details=original['order_details']
    )


def orders_dynamic_filter(request, lookup):
    auth_interface = WaitressAuth()
    waitress = ClientManager(request, is_waitress=True)
    visitor = ClientManager(request, is_waitress=False)

    if not waitress.true_waitress and not visitor.true_visitor:
        return auth_interface.authenticate()

    action_log_data = get_action_log_data({'waitress_status': {'$ne': 'C'}}, 'restaurant_id')
    if not action_log_data:
        abort(HTTPStatus.FORBIDDEN, 'Смена закрыта')

    client = waitress if waitress.true_waitress else visitor
    if not client.is_waitress:
        visitor_data = {key: val for key, val in client.get_client_data().items() if key in ('hall', 'table')}
        lookup.update(visitor_data)

    lookup.update(action_log_data)
