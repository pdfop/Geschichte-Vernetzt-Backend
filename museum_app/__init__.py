from flask import Flask
import os
from flask_graphql import GraphQLView
from flask_graphql_auth import GraphQLAuth
from .extensions import mongo
from museum_app.api import api
from app.API import graphql_schema

"""
    Main App Factory function 
    registers blueprints of endpoints to the app
    binds the JWT sessions to the app
"""


def create_app(config_object='museum_app.settings'):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    mongo.init_app(app)
    auth = GraphQLAuth(app)
    # GraphiQl Binds
    app.add_url_rule(
        '/api/graphql',
        view_func=GraphQLView.as_view(
            'usergraphql',
            schema=graphql_schema,
            graphiql=True
        )
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # landing page for entire app
    @app.route('/')
    def hello():
        return 'Hello World!'

    # adding blueprints for endpoints
    app.register_blueprint(api)

    return app

