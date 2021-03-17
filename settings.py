from os import environ

from collection_schemas import FOOD_CATEGORY_SOLID_TREE, ACTION_LOG, ORDER
from authentication import WaitressAuth

# region EVE settings
DEBUG = environ.get('DEBUG', default=True)

X_DOMAINS = '*'
X_HEADERS = ['Authorization', 'Content-type']

HATEOAS = False

IF_MATCH = False
ENFORCE_IF_MATCH = False
CACHE_CONTROL = 'no-cache'

PAGINATION = False

# endregion

# region Database
MONGO_HOST = environ.get('MONGO_DB_HOST', default='restaurant')
MONGO_PORT = int(environ.get('MONGO_DB_PORT', default=27017))
MONGO_USERNAME = environ.get('MONGO_DB_USERNAME', default='restaurant_user')
MONGO_PASSWORD = environ.get('MONGO_DB_PASSWORD', default='restaurant_passw0rd')
MONGO_DBNAME = environ.get('MONGO_DB_DBNAME', default='restaurant_database')

# endregion

# region Data schema
DOMAIN = {
    'food_category': {
        'schema': FOOD_CATEGORY_SOLID_TREE,
        'resource_methods': ['GET'],
        'item_methods': [],
    },
    'orders': {
        'schema': ORDER,
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['PATCH'],
    },
    'action_log': {
        'schema': ACTION_LOG,
        'resource_methods': ['GET', 'POST'],
        'item_methods': ['PATCH'],
        'authentication': WaitressAuth
    }
}
# endregion
