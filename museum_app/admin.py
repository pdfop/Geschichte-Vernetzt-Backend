import json
from flask import Blueprint, request
from app.AdminSchema import admin_schema

"""
Endpoint for the admin portal. 
serves app.AdminSchema.admin_schema
"""
admin = Blueprint('admin', __name__, template_folder="models", url_prefix='/admin')


@admin.route('/', methods=['POST'])
def admin_endpoint():
    """Endpoint Serving the Admin Schema. Accepts POST requests at /admin/ and returns the result in json"""
    data = json.loads(request.data)
    return json.dumps(admin_schema.execute(data['query']).data)

