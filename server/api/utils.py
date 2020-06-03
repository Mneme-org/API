from datetime import datetime, timedelta
from functools import wraps

from server.api import app
from server.api.models import User

from flask import request, jsonify
import jwt


def generate_auth_token(pub_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'public_id': pub_id,
            'exp': datetime.now() + timedelta(minutes=30)
        }
        token = jwt.encode(payload, app.config['SECRET_KEY'])
        return str(token)
    except Exception as e:
        return e

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token', None)

        if token is None:
            return jsonify({'message': 'Token is required!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        if not user:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(user, *args, **kwargs)

    return decorated