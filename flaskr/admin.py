from flask import Blueprint, session, request, g
from werkzeug.security import generate_password_hash, check_password_hash
from models.Admin import Admin
from models.Code import Code
import string
import random
"""
Subapp to handle admin portal. 
Creates and manages admin accounts. 
Creates and manages promotion codes. 
Contains admin functionality 
"""
admin = Blueprint('admin', __name__, template_folder="models", url_prefix='/admin')


@admin.before_app_request
def load_session():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = Admin.objects.get(username=user_id)


@admin.route('/create', methods=['POST'])
def create_admin():
    username = request.form['username']
    password = request.form['password']
    if not Admin.objects(username=username):
        account = Admin(username=username, password=generate_password_hash(password))
        account.save()
        return "Account created!"
    else:
        return "Name taken!"


@admin.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if not Admin.objects(username=username):
        return "Account not found!"
    else:
        account = Admin.objects.get(username=username)
        if check_password_hash(account.password, password):
            session.clear()
            session['user_id'] = account.username
            return "Logged in as Admin:{}".format(account.username)
        else:
            return "Wrong Password!"


@admin.route('/update', methods=['POST'])
def change_password():
    username = request.form['username']
    password = request.form['password']
    if not Admin.objects(username=username):
        return "Account not found!"
    else:
        account = Admin.objects.get(username=username)
        account.update(password=generate_password_hash(password))
        return "Success"


@admin.route('/generate')
def generate():
    letters = string.ascii_letters
    rd = ''.join(random.choice(letters) for i in range(6))
    code = Code(code=rd)
    code.save()
    return "Created Code {}".format(rd)
