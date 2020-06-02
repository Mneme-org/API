from datetime import datetime, timedelta

from server.api import app

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