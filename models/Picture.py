from mongoengine import *


class Picture(Document):
    """
    Template for a picture with description in the Database.
    """
    meta = {'db_alias': 'file',
            'collection': 'picture'}
    picture = FileField(content_type='image/png')
    description = StringField()
