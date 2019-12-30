from flask import Flask
import os
from flask_graphql import GraphQLView
from flask_graphql_auth import GraphQLAuth
from .user import user
from .obj import obj
from .extensions import mongo
from .admin import admin


def create_app(config_object='flaskr.settings'):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    mongo.init_app(app)
    auth = GraphQLAuth(app)
    # GraphQl Bind
    from app.UserSchema import user_schema
    from app.AdminSchema import admin_schema
    from app.TourSchema import tour_schema
    app.add_url_rule(
        '/user/graphql',
        view_func=GraphQLView.as_view(
            'usergraphql',
            schema=user_schema,
            graphiql=True
        )
    )
    app.add_url_rule(
        '/admin/graphql',
        view_func=GraphQLView.as_view(
            'admingraphql',
            schema=admin_schema,
            graphiql=True
        )
    )
    app.add_url_rule(
        '/tour/graphql',
        view_func=GraphQLView.as_view(
            'tourgraphql',
            schema=tour_schema,
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

    # adding blueprints for subapps
    app.register_blueprint(user)
    app.register_blueprint(obj)
    app.register_blueprint(admin)
    return app

