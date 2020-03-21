from mongoengine import *


class Admin(Document):
    """
        Template for an admin account in the Database.
    """
    meta = {'db_alias': 'user',
            'collection': 'admin'}
    username = StringField(required=True)
    password = StringField(required=True)
