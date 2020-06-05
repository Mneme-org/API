from datetime import datetime, timedelta

from . import crud
from . import SECRET_KEY, pwd_context, ALGORITHM
import jwt


def generate_auth_token(pub_id: str, expires_delta: timedelta = None):
    expires = datetime.utcnow() + (expires_delta or timedelta(minutes=30))

    payload = {
        'public_id': pub_id,
        'exp': expires
    }
    encoded_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_token

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.headers.get('x-access-token', None)
#
#         if token is None:
#             return jsonify({'message': 'Token is required!'}), 401
#
#         try:
#             data = jwt.decode(token, SECRET_KEY)
#             user = crud.get_user_by_pub_id(db, data['public_id'])
#         except:
#             return jsonify({'message': 'Token is invalid'}), 401
#
#         if not user:
#             return jsonify({'message': 'Token is invalid'}), 401
#
#         return f(user, *args, **kwargs)
#
#     return decorated

def auth_user(username, password, db):
    """returns False if not authenticated, else returns user"""
    user = crud.get_user_by_username(db, username)
    if  user is None:
        return False

    if pwd_context.verify(password, user.hashed_password):
        return user
    else:
        return False