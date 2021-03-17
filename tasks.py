from huey import RedisHuey
from huey import crontab

from infrastructure import LandAPIInterface, close_conductor_session

huey = RedisHuey()

# region merge MingoDb with Supervisor DB
land_api = LandAPIInterface()


@huey.periodic_task(crontab(minute='*/30'))
def pull_menu_periodic():
    land_api.pull_menu()


@huey.periodic_task(crontab(minute='*/10'))
def push_orders_periodic():
    land_api.push_orders()


@huey.periodic_task(crontab(minute='*/10'))
def push_microservice_logs_periodic():
    land_api.push_microservice_logs()


@huey.periodic_task(crontab(minute='*/10'))
def push_waitress_log_periodic():
    land_api.push_waitress_log()


@huey.periodic_task(crontab(minute='*/10'))
def push_order_logs_periodic():
    land_api.push_order_logs()
# endregion
