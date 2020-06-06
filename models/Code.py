from mongoengine import *


class Code(Document):
    """
        Template for a promotion code in the Database.
    """
    meta = {'db_alias': 'user',
            'collection': 'code'}
    # codes are generated as random 5 character strings and automatically deleted when used
    code = StringField(required=True, primary_key=True)

