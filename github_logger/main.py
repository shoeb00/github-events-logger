import json

from flask import Flask
from flask import request
from flask_pymongo import PyMongo

app = Flask(__name__)

MAX_RECORD_LIMIT = 20

try:
    mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/myDatabase")
    db = mongodb_client.db
    collection = db['myDatabase']
    # collec.insert({'author' : res['commits'][0]['author']})

except Exception as e:
    print('error connecting to the DB', e)


@app.route('/github', methods=['POST'])
def index():
    if request.headers['Content-Type'] == 'application/json':
        res = request.json
        message = extract(res)
        print(len(message), message)
        if len(message) > 0:
            k = collection.insert_one(message)
            print(k)
        return str(res)


@app.route('/actions', methods=['GET'])
def root():
    page = request.args.get('page', default=1, type=int)
    lastId = request.args.get('id', default="", type=str)
    query = {}
    if page == 0 and lastId != "":
        query = {"_id": {"$gt": lastId}}
    if page != 0 and lastId != "":
        query = {"_id": {"$lt": lastId}}

    data = []
    for i in collection.find(query).limit(MAX_RECORD_LIMIT):
        data.append(i)

    return json.dumps(data)


def extract(data):
    if "commits" in data and len(data["commits"]) > 0:
        return push_request(data)
    elif 'Merge pull request' in data['head_commit']['message']:
        return merge_request(data)
    elif "pull_request" in data and data['action'] == 'opened' and data['pull_request']['merged'] is False:
        return pull_request(data)
    else:
        pass


def push_request(data):
    author = str(data['commits'][0]['author']['name'])
    repo = str(data['ref'])
    i = len(repo) - 1
    to_branch = ''
    while repo[i] != '/':
        to_branch += repo[i]
        i -= 1
    to_branch = to_branch[::-1]
    timestamp = data['commits'][0]['timestamp']
    # todo change timestamp to UTC
    message = '"' + author + '" pushed to "' + to_branch + '" on ' + timestamp
    action = {'push_request': message}
    return action


def pull_request(data):
    author = data['pull_request']['base']['user']['login']
    from_branch = data['pull_request']['head']['ref']
    to_branch = data['pull_request']['base']['ref']
    created_time = data['pull_request']['created_at']
    updated_at = data['pull_request']['updated_at']
    message = '"' + author + '" submitted a pull request from "' + from_branch + \
              '" to "' + to_branch + '" on ' + created_time
    action = {'pull_request': message}
    return action


def merge_request(data):
    author = data['sender']['login']
    from_branch = data['pull_request']['head']['ref']
    to_branch = data['pull_request']['base']['ref']
    created_time = data['pull_request']['base']['repo']['created_at']
    updated_at = data['pull_request']['updated_at']
    message = '"' + author + '" merge branch "' + from_branch + '" to "' + to_branch + '" on ' + created_time
    action = {'merge_request': message}
    print(action)
    return action


if __name__ == "__main__":
    app.run(port=3000, debug=True)
