from mongoengine import *
from models.Question import Question
from models.User import User


class Answer(Document):
    """
        Template for an answer in the Database.
    """
    meta = {'db_alias': 'tour',
            'collection': 'answer'}
    question = ReferenceField(document_type=Question, required=True)
    user = ReferenceField(document_type=User, required=True)
    answer = StringField(required=True)
