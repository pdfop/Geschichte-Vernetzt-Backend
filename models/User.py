from mongoengine import *


class User(Document):
    """
        Template for a user in the Database.
    """
    meta = {'db_alias': 'user',
            'collection': 'user'}
    username = StringField(required=True)
    password = StringField(required=True)
    producer = BooleanField(default=False)

