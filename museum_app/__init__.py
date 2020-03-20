import json

from flask import Flask
from flask_cors import CORS
from flask_graphql_auth import GraphQLAuth
import os
from .extensions import mongo
from app.Schema import web_schema, app_schema
from graphene_file_upload.flask import FileUploadGraphQLView


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
    #@app.route('/web/cors', methods=['POST', 'GET'])
    #@cross_origin(supports_credentials=True)
    #def cors_endpoint():
    #    data = json.loads(request.data)
    #    return json.dumps(web_schema.execute(data['query'])).data

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
    return app

