from datetime import datetime, timedelta
import jwt


def generate_auth_token(pub_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=35),
            'iat': datetime.utcnow(),
            'sub': pub_id
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e