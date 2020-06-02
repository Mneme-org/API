from flask import Flask, request
from flask_restful import Resource, reqparse, marshal_with, fields, abort
from flask_sqlalchemy import SQLAlchemy

from server.api import app, api_
# from flaskblog.models import

ENTRIES = {
    'entry1': {'entry': 'build an API'},
    'entry2': {'entry': '?????'},
    'entry3': {'entry': 'profit!'},
}

def abort_if_entry_doesnt_exist(entry_id):
    if entry_id not in ENTRIES:
        abort(404, message=f'Entry {entry_id} does not exist!')

parser = reqparse.RequestParser()
parser.add_argument('entry')

class EntriesList(Resource):
    def get(self):
        return ENTRIES

    def post(self):
        args = parser.parse_args()
        entry_id = int(max(ENTRIES.keys()).lstrip('entry')) + 1
        entry_id = 'entry%i' % entry_id
        ENTRIES[entry_id] = {'entry': args['entry']}
        return ENTRIES[entry_id], 201

class Entry(Resource):
    def get(self, entry_id):
        abort_if_entry_doesnt_exist(entry_id)
        return ENTRIES[entry_id]

    def delete(self, entry_id):
        abort_if_entry_doesnt_exist(entry_id)
        del ENTRIES[entry_id]
        return 'Deleted!', 204

    def put(self, entry_id):
        args = parser.parse_args()
        entry = {'entry': args['entry']}
        ENTRIES[entry_id] = entry
        return entry, 201

api_.add_resource(Entry, '/entries/<entry_id>')
api_.add_resource(EntriesList, '/entries')

if __name__ == '__main__':
    app.run(debug=True)
