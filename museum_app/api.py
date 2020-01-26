import json
from flask import Blueprint, request
from app.API import graphql_schema

""" 
Endpoint for tour management 
serves app.TourSchema.tour_schema 
"""
api = Blueprint('tour', __name__, template_folder="models", url_prefix='/api')


@api.route('/', methods=['POST'])
def api_endpoint():
    """Endpoint for the Tour schema. Accepts POST requests at /tour/ and returns the results in json. """
    data = json.loads(request.data)
    return json.dumps(graphql_schema.execute(data['query']).data)

