from mongoengine import *


class MuseumObject(Document):
    """
    Template for an object in the Database.
    """
    object_id = IntField(required=True, primary_key=True)
    category = StringField(required=True)
    sub_category = StringField(required=True)
    meta = {'db_alias': 'object',
            'collection': str(sub_category)}
    title = StringField(required=True)
    year = IntField()
    picture = URLField()
    art_type = StringField()
    creator = StringField()
    material = StringField()
    # size is defined as "height x width x depth" in cm
    size = StringField()
    location = StringField()


# TODO: test if collection switch works

