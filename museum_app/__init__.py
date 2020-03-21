import json
from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_graphql_auth import GraphQLAuth
import os
from .extensions import mongo
from app.Schema import web_schema, app_schema
from graphene_file_upload.flask import FileUploadGraphQLView
from museum_app.file import fileBP


def create_app(config_object='museum_app.settings'):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    mongo.init_app(app)
    # flask-graphql-auth bind
    auth = GraphQLAuth(app)
    # flask-cors bind
    cors = CORS(app, resources={r"/*": {"origins": "http://localhost:8081"}}, supports_credentials=True)

    # Endpoints
    app.add_url_rule(
        '/web/',
        view_func=FileUploadGraphQLView.as_view(
            'web',
            schema=web_schema,
            # TODO: set to false for production
            graphiql=True
        )
    )
    app.add_url_rule(
        '/app/',
        view_func=FileUploadGraphQLView.as_view(
            'app',
            schema=app_schema,
            # TODO: set to false for production
            graphiql=True
        )
    )
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # TODO: remove for production
    # landing page for entire app
    @app.route('/')
    def hello():
        return 'Hello World!'

    # TODO:
    #   remove, use for testing if cors is still broken
    @app.route('/web/cors', methods=['POST', 'GET'])
    @cross_origin(supports_credentials=True)
    def cors_endpoint():
        data = json.loads(request.data)
        return json.dumps(web_schema.execute(data['query']).data)

    app.register_blueprint(fileBP)
    return app

