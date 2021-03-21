### About
    Demo project based on Python EVE framework which shows simple and 
    gracefull developing of RESTful application.
### Structure
    By using MongoDB database we need just describe database collection 
    shemas in python file collection_shemas.py
```
   ORDER = {
    'microservice_type': {
        'type': 'string',
        'default': MICROSERVICE_TYPE,
        'required': False,
    },
    'restaurant_id': {
        'type': 'integer',
        'allowed': RESTAURANT_CHOICES,
        'required': False,
        'unique': False,
    },
    'ip': {
        'type': 'string',
        'minlength': 8,
        'maxlength': 39,
        'required': False,
        'unique': False,
        'default': '127.0.0.1',
    }
    ...
    }
```
    Allowed method are declared inside DOMAIN with refereces to 
    shemas in settins.py
```
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
            ...
        }
    }
```
    Validation for POST/PATCH/PUT requests JSON data will be provided by 
    built-in Validator() class. Data serialization-deserialization works 
    same right out of the box.
    To apply addition actions while processing requests Event Hooks can be used:
```
    application.on_insert_action_log += open_waitress_session_actions
    application.on_update_action_log += change_waitress_session_actions
    
    application.on_insert_orders += new_order_actions
    application.on_update_orders += close_order_actions
    
    application.on_pre_GET_orders += orders_dynamic_filter
```