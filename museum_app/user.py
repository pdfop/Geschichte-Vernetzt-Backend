from flask import Blueprint, request
import json
from app.UserSchema import user_schema
"""
Endpoint for user account creation 
serves app.UserSchema.user_schema
"""

user = Blueprint('user', __name__, template_folder='models', url_prefix='/user')


@user.route('/', methods=['POST'])
def user_endpoint():
    data = json.loads(request.data)
    return json.dumps(user_schema.execute(data['query']).data)

