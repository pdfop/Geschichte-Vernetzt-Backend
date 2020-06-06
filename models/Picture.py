from mongoengine import *


class Picture(Document):
    """
    Template for a picture with description in the Database.
    """
    meta = {'db_alias': 'file',
            'collection': 'picture'}
    picture = FileField(content_type='image/jpeg')
    # currently not used anymore.
    description = StringField()
