from mongoengine import *


class MuseumObject(Document):
    """
    Template for an object in the Database.
    """
    object_id = StringField(required=True, primary_key=True)
    category = StringField(required=True)
    sub_category = StringField(required=True)
    meta = {'db_alias': 'object',
            'collection': 'object'}
    title = StringField(required=True)
    year = ListField(StringField())
    # TODO: change this to URL field after testing
    picture = ListField(StringField())
    art_type = ListField(StringField())
    creator = ListField(StringField())
    material = ListField(StringField())
    # size is defined as "height x width x depth" in cm
    size = StringField()
    location = ListField(StringField())
    description = StringField()
    interdisciplinary_context = StringField()


