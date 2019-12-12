from mongoengine import *


class Question(Document):
    """
        Template for a question in the Database.
    """
    meta = {'db_alias': 'tour',
            'collection': 'question'}
    question = StringField(required=True)
    linked_objects = ListField()
