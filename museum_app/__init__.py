from flask import Flask, request
import io
from flask_graphql import GraphQLView
from flask_graphql_auth import GraphQLAuth
import os

from models.Picture import Picture
from .extensions import mongo
from museum_app.web import web as web_blueprint
from museum_app.app import app as app_blueprint
from app.Schema import web_schema, app_schema
from graphene_file_upload.flask import FileUploadGraphQLView


def create_app(config_object='museum_app.settings'):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    mongo.init_app(app)
    auth = GraphQLAuth(app)
    # GraphiQl Binds
    app.add_url_rule(
        '/web/graphql',
        view_func=FileUploadGraphQLView.as_view(
            'webgraphql',
            schema=web_schema,
            graphiql=True
        )
    )
    app.add_url_rule(
        '/app/graphql',
        view_func=FileUploadGraphQLView.as_view(
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


# TODO: delete this when im done referencing it
  #  from flask import send_file
   # @app.route('/upload/', methods=['POST'])
    #def upload():
     #   f = request.files['file']
      #  pic = Picture(description="ne")
       # pic.picture.put(f, content_type='image/png')
        #pic.save()
        #pic.reload()
        #raw = pic.picture.read()

       # return send_file(io.BytesIO(raw),
      #                   attachment_filename='logo.png',
       #                  mimetype='image/png')

    #@app.route('/getfile',methods=['GET'])
    #def getfile():
     #   pic = Picture.objects.get(id="5e6f9535e980580baec1e28f")
      #  raw = pic.picture.read()
       # return send_file(io.BytesIO(raw),
        #                 attachment_filename='logo.png',
         #                mimetype='image/png')
    # adding blueprints for endpoints
    app.register_blueprint(app_blueprint)
    app.register_blueprint(web_blueprint)
    return app

