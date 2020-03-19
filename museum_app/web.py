import json
from flask import Blueprint, request
from app.Schema import web_schema

""" 
Endpoint the web portal
serves app.Schema.web_schema
"""
web = Blueprint('web', __name__, template_folder="models", url_prefix='/web')


@web.route('/', methods=['POST', 'GET'])
def web_endpoint():
    """Endpoint for the web schema. Accepts POST requests at /web/ and returns the results in json. """
    data = json.loads(request.data)
    return json.dumps(web_schema.execute(data['query']).data)
