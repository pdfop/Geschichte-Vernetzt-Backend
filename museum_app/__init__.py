from flask import Flask
import os
from flask_graphql import GraphQLView
from flask_graphql_auth import GraphQLAuth
from .extensions import mongo
from museum_app.web import web as web_blueprint
from museum_app.app import app as app_blueprint
from app.Schema import web_schema, app_schema


def create_app(config_object='museum_app.settings'):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    mongo.init_app(app)
    auth = GraphQLAuth(app)
    # GraphiQl Binds
    app.add_url_rule(
        '/web/graphql',
        view_func=GraphQLView.as_view(
            'webgraphql',
            schema=web_schema,
            graphiql=True
        )
    )
    app.add_url_rule(
        '/app/graphql',
        view_func=GraphQLView.as_view(
            'appgraphql',
            schema=app_schema,
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
    app.register_blueprint(app_blueprint)
    app.register_blueprint(web_blueprint)
    return app

