from functools import wraps

import bcrypt
from eve.auth import BasicAuth
from flask import request

from constants import (
    WAITRESS_LOGIN,
    WAITRESS_PASSWORD_HASH,
    SUPERVISOR_SERVICE_API_LOGIN,
    SUPERVISOR_SERVICE_API_LOGIN_PASSWORD
)


class WaitressAuth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource, method):
        return username == WAITRESS_LOGIN and bcrypt.checkpw(password, WAITRESS_PASSWORD_HASH)


def land_api_auth():
    return SUPERVISOR_SERVICE_API_LOGIN, SUPERVISOR_SERVICE_API_LOGIN_PASSWORD


def route_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_interface = WaitressAuth()

        auth_header = request.authorization

        if auth_header is None:
            return auth_interface.authenticate()

        if not auth_interface.check_auth(auth_header.username, auth_header.password, None, None, None):
            return auth_interface.authenticate()

        return f(*args, **kwargs)

    return decorated
