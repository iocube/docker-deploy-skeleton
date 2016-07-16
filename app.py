import os

import flask
from flask import Flask
import pymongo

# for debugging purpose only. values should be seen when running 'docker-compose logs web'.
print('DATABASE_HOST', os.getenv('DATABASE_HOST'))
print('DATABASE_NAME', os.getenv('DATABASE_NAME'))
print('DATABASE_USER', os.getenv('DATABASE_USER'))
print('DATABASE_PASSWORD', os.getenv('DATABASE_PASSWORD'))

client = pymongo.MongoClient(os.getenv('DATABASE_HOST'))
client[os.getenv('DATABASE_NAME')].authenticate(
    os.getenv('DATABASE_USER'),
    os.getenv('DATABASE_PASSWORD'),
    mechanism='SCRAM-SHA-1'
)

app = Flask(__name__)


@app.route('/')
def index():
    return 'Flask: {0}'.format(flask.__version__)


@app.route('/database')
def database():
    # fetch user from 'users' collection inside 'webapp' database.
    user = client.webapp.users.find_one()
    return str(user)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)