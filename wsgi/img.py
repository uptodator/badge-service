#!/usr/bin/python
# -*- coding: utf8 -*-

import os
from flask import Flask, request
from flask.ext.restful import Resource, Api
from flask.ext.pymongo import PyMongo

SHIELDS_IO_URL = "http://img.shields.io/badge/uptodator-{0}-{1}.svg"

COLOR_OK = 'green'
MSG_OK = 'deps up to date'

COLOR_WARNING = 'red'
MSG_WARNING = '{0} outdated'

app = Flask(__name__)
api = Api(app)

app.config['PROPAGATE_EXCEPTIONS'] = True

app.config['MONGO_HOST'] = os.getenv('OPENSHIFT_MONGODB_DB_HOST')
app.config['MONGO_PORT'] = os.getenv('OPENSHIFT_MONGODB_DB_PORT')
app.config['MONGO_DBNAME'] = 'python'
app.config['MONGO_USERNAME'] = os.getenv('OPENSHIFT_MONGODB_DB_USERNAME')
app.config['MONGO_PASSWORD'] = os.getenv('OPENSHIFT_MONGODB_DB_PASSWORD')
app.config['MONGO_DBNAME'] = 'python'

mongo = PyMongo(app)


class Badge(Resource):

    def get(self, project_id):
        project = mongo.db.deps.find_one_or_404({'appId': project_id})
        if not project['numberOfUpdates'] > 0:
            badge_url = SHIELDS_IO_URL.format(
                MSG_OK.replace(' ', '_'),
                COLOR_OK)
        else:
            badge_url = SHIELDS_IO_URL.format(
                MSG_WARNING.format(project['numberOfUpdates']).replace(' ', '_'),
                COLOR_WARNING)
        return {}, 302, {'Location': badge_url}


class Dependencies(Resource):

    def validate_request_body(self, json):
        if not isinstance(json, dict):
            return False
        if set(json.keys()) != {'appId', 'numberOfUpdates'}:
            return False
        return True

    def post(self):
        deps_status = request.get_json(force=True)
        if not self.validate_request_body(deps_status):
            return 'Invalid request', 400
        update_result = mongo.db.deps.find_and_modify(
            query={'appId': deps_status['appId']},
            update={"$set": {"numberOfUpdates": int(deps_status['numberOfUpdates'])}},
            upsert=True,
            full_response=True,
            new=False
        )
        if update_result['ok'] != 1:
            return 'Error while updating dependencies status!', 500
        return 'Dependencies updated', 201


api.add_resource(Dependencies, '/dependencies/update')
api.add_resource(Badge, '/<string:project_id>')


if __name__ == '__main__':
    app.run(debug=True)
