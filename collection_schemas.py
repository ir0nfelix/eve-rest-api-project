from constants import (
    MICROSERVICE_TYPE,
    ORDER_STATUS_CHOICES,
    HALL_CHOICES,
    RESTAURANT_CHOICES,
    TABLE_CHOICES,
    MICROSERVICE_ACTION_CHOICES,
    WAITER_STATUS_CHOICES,
    LANGUAGE_CHOICES,
    ORDER_CANCEL_SOURCE,
    DEPOSIT_VALUE,
    WAITER_SESSION_CLOSE_SOURCE
)


# region Base Schemas
RESTAURANT_BASE_LOG = {
        'action_datetime': {
            'type': 'string',
            'required': True,
        },
        'microservice_type': {
            'type': 'string',
            'default': MICROSERVICE_TYPE,
            'required': True,
        },
        'restaurant_id': {
            'type': 'integer',
            'allowed': RESTAURANT_CHOICES,
            'required': True,
            'nullable': True,
        }
}

CLIENT_DEVICE_BASE_LOG = {
        'ip': {
            'type': 'string',
            'minlength': 8,
            'maxlength': 39,
            'required': True,
            'nullable': True

        },
        'mac': {
            'type': 'string',
            'minlength': 12,
            'maxlength': 17,
            'required': True,
            'nullable': True

        },
    }

# endregion


# region Food Schemas
FOOD_CATEGORY_SOLID_TREE = {
    'id': {
        'type': 'integer',
        'required': True,
        'unique': True
    },
    'name_ru': {
        'type': 'string',
        'minlength': 3,
        'maxlength': 100,
        'required': True,
        'unique': True,
    },
    'name_en': {
        'type': 'string',
        'minlength': 0,
        'maxlength': 100,
        'required': False,
        'unique': False,
    },
    'name_ch': {
        'type': 'string',
        'minlength': 0,
        'maxlength': 100,
        'required': False,
        'unique': False,
    },
    'order_id': {
        'type': 'integer',
        'default': 100,
    },

    'foods': {
        'type': 'list',  # foods relation
        'default': [],
        'schema': {
            'code': {
                'type': 'integer',
                'min': 1,
                'max': 999,
                'required': True,
                'unique': True
            },
            'name_ru': {
                'type': 'string',
                'minlength': 4,
                'maxlength': 255,
                'required': True,
                'unique': True
            },
            'description_ru': {
                'type': 'string',
                'minlength': 0,
                'maxlength': 500,
                'required': True,
                'unique': False
            },
            'description_en': {
                'type': 'string',
                'minlength': 0,
                'maxlength': 500,
                'required': False,
                'unique': False
            },
            'description_ch': {
                'type': 'string',
                'minlength': 0,
                'maxlength': 500,
                'required': False,
                'unique': False
            },
            'picture': {
                'type': 'string',
                'minlength': 0,
                'maxlength': 255,
                'required': True,
                'unique': True
            },
            'picture_big': {
                'type': 'string',
                'minlength': 0,
                'maxlength': 255,
                'required': True,
                'unique': True
            },
            'is_vegan': {
                'type': 'boolean',
                'default': False
            },
            'is_special': {
                'type': 'boolean',
                'default': False
            },
            'cost': {
                'type': 'float',
                'min': 0.01,
                'max': 99999.99,
                'required': True,
                'unique': False
            },

            'in_stock': {
                'type': 'boolean',
                'default': True,
                'required': False,
            }
        }
    }
    }

# endregion


# region Order Schemas
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
    },
    'mac': {
        'type': 'string',
        'minlength': 12,
        'maxlength': 17,
        'required': False,
        'unique': False,
        'nullable': True
    },
    'status': {
        'type': 'string',
        'allowed': ORDER_STATUS_CHOICES,
        'required': False,
        'unique': False,
    },
    'cancel_source': {
        'type': 'string',
        'allowed': ORDER_CANCEL_SOURCE,
        'required': False,
        'unique': False,
    },
    'datetime_open': {
        'type': 'string',
        'minlength': 19,
        'maxlength': 19,
        'required': False,
        'unique': False,
    },
    'datetime_close': {
        'type': 'string',
        'minlength': 19,
        'maxlength': 19,
        'required': False,
        'nullable': True,
    },
    'hall': {
        'type': 'integer',
        'allowed': HALL_CHOICES,
        'required': False,
        'unique': False,
    },
    'table': {
        'type': 'integer',
        'allowed': TABLE_CHOICES,
        'required': False,
        'unique': False,
    },
    'lang': {
        'type': 'string',
        'allowed': LANGUAGE_CHOICES,
        'required': False,
        'unique': False,
    },
    'by_cash': {
        'type': 'boolean',
        'required': True,
    },
    'cash_nominal': {
        'type': 'integer',
        'required': False,
    },
    'order_details':
        {'type': 'list',
         'schema': {
             'type': 'dict',
             'schema': {
                 'cost': {
                     'type': 'integer',
                     'min': 1,
                     'max': 100000,
                     'required': True,
                     'unique': False
                 },
                 'qty': {
                     'type': 'integer',
                     'min': 1,
                     'max': 100,
                     'required': True,
                     'unique': False
                 },
                 'item': {
                     'type': 'integer',
                     'min': 1,
                     'max': 999,
                     'required': True,
                     'unique': False
                 },
             }
         }
         }
}

# endregion


# region Logs schemas
BISTRO_LAST_MODIFIED = {
    'schema': {
        'bistro_last_modified': {
            'type': 'integer',
        },
    }
}


ACTION_LOG = {
    'restaurant_id': {
        'type': 'integer',
        'allowed': RESTAURANT_CHOICES,
        'required': True,
    },
    'waitress_status': {
        'type': 'string',
        'allowed': WAITER_STATUS_CHOICES,
        'required': True,
    },
    'departure_time': {
        'type': 'string',
        'minlength': 19,
        'maxlength': 19,
        'required': True,
    },
    'arrival_time': {
        'type': 'string',
        'minlength': 19,
        'maxlength': 19,
        'required': True,
    },
    'session_datetime_open': {
        'type': 'string',
        'minlength': 19,
        'maxlength': 19,
        'readonly': True,
        'required': False,
    },
    'session_datetime_close': {
        'type': 'string',
        'minlength': 19,
        'maxlength': 19,
        'empty': True,
        'readonly': True,
        'required': False,
    },
}


MICROSERVICE_LOG = {
    'request': {
        'type': 'string',
        'allowed': MICROSERVICE_ACTION_CHOICES,
        'required': True,
    },
    'response_code': {
        'type': 'integer',
        'min': 100,
        'max': 999,
        'required': False,
        'nullable': True,
    },
    'response': {
        'type': 'dict',
        'required': False,

    }
}
MICROSERVICE_LOG.update(RESTAURANT_BASE_LOG)


ORDER_LOG = {
        'hall': {
            'type': 'integer',
            'allowed': HALL_CHOICES,
            'required': False,
            'unique': False,
        },
        'table': {
            'type': 'integer',
            'allowed': TABLE_CHOICES,
            'required': False,
            'unique': False,
        },
        'status': {
            'type': 'string',
            'default': ORDER_STATUS_CHOICES,
            'required': True,
        },
        'cancel_source': {
            'type': 'string',
            'default': ORDER_CANCEL_SOURCE,
            'required': False,
            'nullable': True,

        },
        'order_details': {
            'type': 'list',
            'required': False,
            'nullable': True,

        }
    }
ORDER_LOG.update(RESTAURANT_BASE_LOG)
ORDER_LOG.update(CLIENT_DEVICE_BASE_LOG)


WAITRESS_LOG = {
        'status': {
            'type': 'string',
            'default': WAITER_STATUS_CHOICES,
            'required': True,
        },
        'cancel_source': {
            'type': 'string',
            'allowed': WAITER_SESSION_CLOSE_SOURCE,
            'required': False,
            'nullable': True,
        }

}
WAITRESS_LOG.update(RESTAURANT_BASE_LOG)
WAITRESS_LOG.update(CLIENT_DEVICE_BASE_LOG)


LOCAL_USERS = {
    'ip': {
        'type': 'string',
        'minlength': 8,
        'maxlength': 39,
        'required': True,
        'nullable': True
    },
    'mac': {
        'type': 'string',
        'minlength': 12,
        'maxlength': 17,
        'required': True,
        'nullable': True
    },
    'hall': {
        'type': 'integer',
        'allowed': HALL_CHOICES,
        'required': True,
        'nullable': True,
    },
    'table': {
        'type': 'integer',
        'allowed': TABLE_CHOICES,
        'required': True,
        'nullable': True,
    },
    'lang': {
        'type': 'string',
        'allowed': LANGUAGE_CHOICES,
        'required': True,
        'default': 'ru'
    },
    'is_service_auth': {
        'type': 'boolean',
        'required': True,
        'default': False
    },
    'is_waitress': {
        'type': 'boolean',
        'default': False
    },
    'is_tablet': {
        'type': 'boolean',
        'default': False
    },
    'is_deposit': {
        'type': 'boolean',
        'default': False
    },
    'current_deposit': {
        'type': 'integer',
        'min': 0,
        'max': DEPOSIT_VALUE,
        'required': True,
    },
}

# endregion

