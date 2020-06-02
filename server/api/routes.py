from flask import request, make_response, jsonify
from server.api import app
from server.api.models import User
from server.api.utils import generate_auth_token

from werkzeug.security import check_password_hash

@app.route('/login', methods=["GET"])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic-realm="Login required"'})

    user = User.query.filter_by(user_name=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic-realm="Login required"'})

    if not check_password_hash(user.password, auth.password):
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic-realm="Login required"'})

    token = generate_auth_token(user.public_id)
    return jsonify({'token': token})


if __name__ == '__main__':
    app.run(debug=True)
