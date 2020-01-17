from mongoengine import *
#from models.MuseumObject import MuseumObject
#from models.Tour import Tour


class User(Document):
    """
        Template for an user object in the Database.
    """
    meta = {'db_alias': 'user',
            'collection': 'user'}
    username = StringField(required=True)
    password = StringField(required=True)
    producer = BooleanField(default=False)
    #favourite_objects = ListField(ReferenceField(document_type=MuseumObject))
    #favourite_tours = ListField(ReferenceField(document_type=Tour))
