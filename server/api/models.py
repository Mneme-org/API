from api import db
import jwt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)

    journals = db.relationship('Journal', backref='user', lazy=True)

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e


class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.Text, nullable=False)

    entries = db.relationship('Entry', backref='journal', lazy=True)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jrnl_id = db.Column(db.Integer, db.ForeignKey('journal.id'))
    short = db.Column(db.Text, nullable=False)
    long = db.Column(db.Text, nullable=True)
    # TODO Figure out a better way to store dates, maybe as strings?
    date = db.Column(db.Integer, nullable=False)

    keywords = db.relationship('Keyword', backref='entry', lazy=True)


class Keyword(db.Model):
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'))
    word = db.Column(db.Text, nullable=False)
