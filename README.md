### About
    Demo project based on Python EVE framework which shows simple and 
    gracefull developing of RESTful application.

### Business Logic
    The project was developed like microservice in distributed backend 
    eco-system. That service provides local backend processing for one
    instance of chain restaurant. Each of restaurant has id humber for 
    identification in SUPERVISOR_SERVICE root-service.
    SUPERVISOR_SERVICE API is a root-backend application, which provides
    food menu updating by GET request and receives POST requests from 
    local restaurants (current application) to save client logs, order
    logs and witress logs. SUPERVISOR_SERVICE database is related type,
    prefer is PostgreSQL. 
    To simplify example requests to SUPERVISOR_SERVICE are secured by
    basic authentication, periodic tasks are managed by Huey Consumer.

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
    Allowed method are declared inside DOMAIN with references to
    schemas in settings.py
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

### Build
```
docker-compose build
```

### Run
```
docker-compose up
```