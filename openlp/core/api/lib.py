import json
from flask import jsonify, Response, request
from functools import wraps
from openlp.core.common.settings import Settings
from openlp.core.common.registry import Registry


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not Settings().value('api/authentication enabled'):
            return f(*args, **kwargs)
        token = request.headers.get('Authorization', '')
        if token == Registry().get('authentication_token'):
            return f(*args, **kwargs)
        else:
            return '', 401
    return decorated


def old_success_response():
    return jsonify({'results': {'sucess': True}})


def extract_request(json_string, name):
    try:
        if json_string:
            return json.loads(json_string)['request'][name]
    except KeyError:
        pass
    return None


# ----------------------- OLD AUTH SECTION ---------------------
def check_auth(username, password):
    return Settings().value('api/user id') == username and \
        Settings().value('api/password') == password


def old_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not Settings().value('api/authentication enabled'):
            return f(*args, **kwargs)
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response('', 401, {'WWW-Authenticate': 'Basic realm="OpenLP Login Required"'})
        else:
            return f(*args, **kwargs)
    return decorated
