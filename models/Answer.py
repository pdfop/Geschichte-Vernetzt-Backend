from mongoengine import *
from models.Question import Question
from models.User import User


class Answer(Document):
    """
        Template for an answer in the Database.
    """
    meta = {'db_alias': 'tour',
            'collection': 'answer'}
    answer_id = IntField(required=True, primary_key=True)
    question = ReferenceField(document_type=Question, required=True)
    user = ReferenceField(document_type=User, required=True)
    answer = StringField(required=True)

