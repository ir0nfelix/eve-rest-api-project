from http import HTTPStatus

from eve import Eve
from flask import request, jsonify, current_app

from authentication import route_auth
from event_hooks import (
    open_conductor_session_actions,
    change_conductor_session_actions,
    new_order_actions,
    close_order_actions,
    orders_dynamic_filter
)
from infrastructure import get_action_log_data, ClientManager

application = Eve()

# region Custom endpoint
@application.route('/visitors/')
def get_visitor_data():
    client = ClientManager(request, is_waitress=False)
    return client.get_client_data_response()


@application.route('/action_log/')
def get_action_log_data():
    return jsonify(get_action_log_data({'waitress_status': 'S'}) or {'waitress_status': 'C'})


@application.route('/food_category/enable/<int:code>', methods=['PATCH'])
@route_auth
def enable_food_by_code(code):
    collection = current_app.data.driver.db['food_category']
    collection.update_one({'foods.code': code}, {'$set': {'foods.$.in_stock': True}}, upsert=True)
    return '', HTTPStatus.NO_CONTENT


@application.route('/food_category/disable/<int:code>', methods=['PATCH'])
@route_auth
def disable_food_by_code(code):
    collection = current_app.data.driver.db['food_category']
    collection.update_one({'foods.code': code}, {'$set': {'foods.$.in_stock': False}}, upsert=True)
    return '', HTTPStatus.NO_CONTENT
# endregion


# region add API Event Hooks
application.on_insert_action_log += open_conductor_session_actions
application.on_update_action_log += change_conductor_session_actions

application.on_insert_orders += new_order_actions
application.on_update_orders += close_order_actions

application.on_pre_GET_orders += orders_dynamic_filter
# endregion


if __name__ == '__main__':
    application.run(host='0.0.0.0')
