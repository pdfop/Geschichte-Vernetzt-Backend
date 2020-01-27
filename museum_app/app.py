import json
from flask import Blueprint, request
from app.Schema import app_schema

""" 
Endpoint the app
serves app.Schema.app_schema
"""
app = Blueprint('app', __name__, template_folder="models", url_prefix='/app')


@app.route('/', methods=['POST'])
def app_endpoint():
    """Endpoint for the app schema. Accepts POST requests at /app/ and returns the results in json. """
    data = json.loads(request.data)
    return json.dumps(app_schema.execute(data['query']).data)
