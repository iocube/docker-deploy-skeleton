import os

import flask
from flask import Flask
import pymongo


client = pymongo.MongoClient(os.getenv('DATABASE_HOST'))

app = Flask(__name__)


@app.route('/')
def index():
    return 'Flask: {0}'.format(flask.__version__)


@app.route('/database')
def database():
    build_info = client.db.command('buildinfo')
    return str(build_info)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)