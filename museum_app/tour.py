import json
from flask import Blueprint, request
from app.TourSchema import tour_schema

""" 
Endpoint for tour management 
serves app.TourSchema.tour_schema 
"""
tour = Blueprint('tour', __name__, template_folder="models", url_prefix='/tour')


@tour.route('/', methods=['POST'])
def tour_endpoint():
    """Endpoint for the Tour schema. Accepts POST requests at /tour/ and returns the results in json. """
    data = json.loads(request.data)
    return json.dumps(tour_schema.execute(data['query']).data)
