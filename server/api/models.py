from api import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)

    journals = db.relationship('Journal', backref='user', lazy=True)


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
