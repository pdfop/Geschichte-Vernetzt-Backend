from mongoengine import *
from models.Question import Question
from models.User import User


class Answer(Document):
    """
        Parent class for Answers.
        Serves as the most basic model for text answers to text questions
        Linked to a Question and a User.
        New Answer types may be added by subclassing this like class NewType(Answer)
    """
    meta = {'db_alias': 'tour',
            'collection': 'answer',
            'allow_inheritance': True
            }
    question = ReferenceField(document_type=Question, required=True, reverse_delete_rule=CASCADE)
    user = ReferenceField(document_type=User, required=True, reverse_delete_rule=CASCADE)
    answer = StringField()
