from flask import Blueprint, request
import json
from app.UserSchema import user_schema
"""
Subapp to handle user management. 
Creates and manages user accounts. Admin accounts managed separately.
Handles teacher account promotion
"""

user = Blueprint('user', __name__, template_folder='models', url_prefix='/user')


# TODO: proper binding


@user.route('/create', methods=['POST'])
def create_user():
    data = json.loads(request.data)
    return json.dumps(user_schema.execute(data['query']).data)


@user.route('/promote', methods=['POST'])
def promote_user():
    data = json.loads(request.data)
    return json.dumps(user_schema.execute(data['query']).data)


@user.route('/update', methods=['POST'])
def change_password():
    data = json.loads(request.data)
    return json.dumps(user_schema.execute(data['query']).data)


@user.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    return json.dumps(user_schema.execute(data['query']).data)
