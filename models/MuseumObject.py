from mongoengine import *
from models.Picture import Picture


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
    time_range = StringField()
    year = ListField(StringField())
    picture = ListField(ReferenceField(document_type=Picture, reverse_delete_rule=PULL))
    art_type = ListField(StringField())
    creator = ListField(StringField())
    material = ListField(StringField())
    size = DictField(default={'height': 0, 'width': 0, 'length': 0, 'diameter': 0})
    location = ListField(StringField())
    description = StringField()
    additional_information = StringField()
    interdisciplinary_context = ListField(StringField())


