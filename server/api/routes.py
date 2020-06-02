import uuid

from server.api import app, db
from server.api.models import User
from server.api.utils import generate_auth_token

from flask import request, make_response, jsonify


@app.route('/login', methods=["GET"])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic-realm="Login required"'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic-realm="Login required"'})

    # Because the api will probably be receiving already hashed passwords
    # This is not final
    if user.password == auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic-realm="Login required"'})

    token = generate_auth_token(user.public_id)
    return jsonify({'token': token})


@app.route('/user', methods=['POST'])
def create_user():
    print(request.get_json())
    print(request.data)
    data = request.get_json(force=True)

    public_id = str(uuid.uuid4())
    user = User(public_id=public_id, username=data['username'], password=data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({'status': '200'})


if __name__ == '__main__':
    app.run(debug=True)
