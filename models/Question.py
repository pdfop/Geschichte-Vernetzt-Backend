from mongoengine import *


class Question(Document):
    """
        Template for a question in the Database.
    """
    meta = {'db_alias': 'tour',
            'collection': 'question'}
    qid = IntField(required=True,primary_key=True)
    question = StringField(required=True)
    linked_objects = ListField()
