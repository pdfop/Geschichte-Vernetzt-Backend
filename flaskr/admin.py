import json
from flask import Blueprint, request
from app.AdminSchema import admin_schema

"""
Subapp to handle admin portal. 
Creates and manages admin accounts. 
Creates and manages promotion codes. 
Contains admin functionality 
"""
admin = Blueprint('admin', __name__, template_folder="models", url_prefix='/admin')


@admin.route('/', methods=['POST'])
def admin_endpoint():
    data = json.loads(request.data)
    return json.dumps(admin_schema.execute(data['query']).data)

