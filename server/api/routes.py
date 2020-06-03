import uuid

from server.api import app, db
from server.api.models import User, Journal
from server.api.utils import generate_auth_token, token_required

from sqlalchemy.exc import IntegrityError
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
    if user.password != auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic-realm="Login required"'})

    token = generate_auth_token(user.public_id)
    return jsonify({'token': token})


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json(force=True)

    public_id = str(uuid.uuid4())
    user = User(public_id=public_id, username=data['username'], password=data['password'])

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        return  jsonify({'message': 'Username already exists'})

    return jsonify({'status': '200'})


@app.route('/journal', methods=['POST'])
@token_required
def create_journal(user):
    data = request.get_json(force=True)

    jrnl = Journal(u_id=user.id, name=data['name'])
    db.session.add(jrnl)
    db.session.commit()

    return jsonify({'status': 200, 'journal_id': jrnl.id})


if __name__ == '__main__':
    app.run(debug=True)
