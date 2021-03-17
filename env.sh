export DEBUG=False

export MONGO_DB_HOST='restaurant'
export MONGO_DB_PORT=27017
export MONGO_DB_USERNAME='restaurant_user'
export MONGO_DB_PASSWORD='restaurant_passw0rd'
export MONGO_DB_DBNAME='restaurant_database'

export WAITRESS_LOGIN='waitress'
export WAITRESS_PASSWORD_HASH=''

export SUPERVISOR_SERVICE_API_LOGIN='supervisor_user'
export SUPERVISOR_SERVICE_API_LOGIN_PASSWORD='supervisor_passw0rd'


export SUPERVISOR_SERVICE_API_MENU_URL='http://some-api.com/api/menu/'
export ORDERS_API_URL='http://some-api.com/api/orders/'
export MS_LOGS_API_URL='https://some-api.com/api/logs/microservice/'
export ORDERS_LOGS_API_URL='https://some-api.com/api/logs/orders/'
export WAITRESS_LOGS_API_URL='https://some-api.com/api/logs/waitress/'

export DEPOSIT_VALUE=2000

export EXTERNAL_API_VISITOR_URL='http://some-external-api.com/api/users/'

export GUNICORN_WORKER_COUNT=2