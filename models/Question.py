from mongoengine import *
from .MuseumObject import MuseumObject


class Question(Document):
    """
        Template for a question in the Database.
    """
    meta = {'db_alias': 'tour',
            'collection': 'question'}
    question_id = IntField(required=True, primary_key=True)
    question = StringField(required=True)
    linked_objects = ListField(ReferenceField(document_type=MuseumObject))
