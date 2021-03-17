from os import environ

# SUPERVISOR API
SUPERVISOR_SERVICE_API_MENU_URL = environ.get('ROOT_SERVER_MENU_URL', default='http://some-api.com/api/menu/')
ORDERS_API_URL = environ.get('ORDERS_API_URL', default='http://some-api.com/api/orders/')

MS_LOGS_API_URL = environ.get('MS_LOGS_API_URL', default='https://some-api.com/api/logs/microservice/')
ORDERS_LOGS_API_URL = environ.get('ORDERS_LOGS_API_URL', default='https://some-api.com/api/logs/orders/')
WAITRESS_LOGS_API_URL = environ.get('WAITRESS_LOGS_API_URL', default='https://some-api.com/api/logs/waitress/')

EXTERNAL_API_VISITOR_URL = environ.get('EXTERNAL_API_VISITOR_URL', default='https://some-api.com/api/users/')
# endregion

# region Constants
DATE_HMS_FORMAT = '%Y-%m-%d %H:%M:%S'
USER_HMS_FORMAT = '%H:%M'

MICROSERVICE_TYPE = 'B'

ORDER_STATUS_CHOICES = ['O', 'D', 'C']
ORDER_CANCEL_SOURCE = ['P', 'C', 'S']

WAITER_STATUS_CHOICES = ['S', 'P', 'C']
WAITER_SESSION_CLOSE_SOURCE = ['M', 'T']

MICROSERVICE_ACTION_CHOICES = ['M', 'O', 'L']

LANGUAGE_CHOICES = ['ru', 'en', 'ch']

# simple id of each restaurant
RESTAURANT_CHOICES = list(range(1, 20))

# simple id of hall and table in each restaurant
HALL_CHOICES = list(range(1, 20))
TABLE_CHOICES = list(range(1, 100))

CLIENT_FAKE_HALL_TABLE = 19, 99
ACTION_LOG_FAKE_RESTAURANT_ID = 19

DEPOSIT_TABLE_NUMBERS = [1, 2]

DEPOSIT_VALUE = int(environ.get('DEPOSIT_VALUE', default=100))
# endregion

# region Auth
WAITRESS_LOGIN = environ.get('WAITRESS_LOGIN', default='waitress')
WAITRESS_PASSWORD_HASH = environ.get('WAITRESS_PASSWORD_HASH', default='')

SUPERVISOR_SERVICE_API_LOGIN = environ.get('SUPERVISOR_SERVICE_API_LOGIN', default='supervisor_user')
SUPERVISOR_SERVICE_API_LOGIN_PASSWORD = environ.get('SUPERVISOR_SERVICE_API_LOGIN_PASSWORD', default='supervisor_passw0rd')
# endregion
