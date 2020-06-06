from mongoengine import *
from models.Picture import Picture


class MuseumObject(Document):
    """
    Template for an object in the Database.
    """
    # object id in the museum
    object_id = StringField(required=True, primary_key=True)
    # 'Abteilung' in the museum. could reasonably be an enum
    category = StringField(required=True)
    # 'Sammlungsbereich' in the museum. could reasonably be an enum as well
    sub_category = StringField(required=True)
    meta = {'db_alias': 'object',
            'collection': 'object'}
    title = StringField(required=True)
    # currently not used by app or web frontend
    time_range = StringField()
    year = StringField()
    picture = ListField(ReferenceField(document_type=Picture, reverse_delete_rule=PULL))
    art_type = StringField()
    creator = StringField()
    material = StringField()
    # has to be named size_ because mongoengine uses size as a query keyword
    size_ = StringField()
    location = StringField()
    description = StringField()
    # also currently not used by frontends
    additional_information = StringField()
    interdisciplinary_context = StringField()


