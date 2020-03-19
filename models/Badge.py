from mongoengine import *


class Badge(Document):
    """
    Template for a user achievement badge in the Database.
    """
    meta = {'db_alias': 'file',
            'collection': 'badge'}
    id = StringField(required=True, primary_key=True)
    name = StringField(required=True)
    picture = FileField(content_type='image/png')
    description = StringField(required=True)
    cost = IntField(required=True)
