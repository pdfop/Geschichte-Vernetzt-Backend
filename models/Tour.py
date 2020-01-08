from mongoengine import *
from models.User import User
from models.Question import Question
from models.MuseumObject import MuseumObject


class Tour(Document):
    """
    Template for a tour in the Database.
    """
    meta = {'db_alias': 'tour',
            'collection': 'tour'}
    name = StringField(required=True)
    owner = ReferenceField(document_type=User, required=True)
    session_id = IntField(required=True)
    referenced_objects = ListField(ReferenceField(document_type=MuseumObject))
    questions = ListField(ReferenceField(document_type=Question))
    answers = DictField()
    users = ListField(ReferenceField(document_type=User))
    status = StringField(default='private')


