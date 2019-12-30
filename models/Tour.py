from mongoengine import *
from models.User import User


class Tour(Document):
    """
    Template for a tour in the Database.
    """
    meta = {'db_alias': 'tour',
            'collection': 'tour'}
    tour_id = IntField(required=True, primary_key=True)
    name = StringField(required=True)
    owner = ReferenceField(document_type=User, required=True)
    referenced_objects = ListField()
    questions = ListField()
    answers = DictField()
    users = ListField()


