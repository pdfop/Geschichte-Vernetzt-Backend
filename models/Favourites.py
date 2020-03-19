from mongoengine import *
from models.User import User
from models.MuseumObject import MuseumObject
from models.Tour import Tour


class Favourites(Document):
    """
        Template for favourites of a user.
        These should ideally be attributes of the user.
        However this results in a 3-way cyclic import between the Tour-Answer-User models that I could'nt resolve in
        any of the ways typically suggested.
    """
    meta = {'db_alias': 'user',
            'collection': 'favourites'}
    user = ReferenceField(document_type=User, reverse_delete_rule=CASCADE, primary_key=True, required=True)
    favourite_tours = ListField(ReferenceField(document_type=Tour, reverse_delete_rule=PULL))
    favourite_objects = ListField(ReferenceField(document_type=MuseumObject, reverse_delete_rule=PULL))


