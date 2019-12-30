from mongoengine import *


class Code(Document):
    """
        Template for a promotion code in the Database.
    """
    meta = {'db_alias': 'user',
            'collection': 'code'}
    code = StringField(required=True, primary_key=True)

