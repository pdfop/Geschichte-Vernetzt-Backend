from mongoengine import *


class Answer(Document):
    """
        Template for an answer in the Database.
    """
    meta = {'db_alias': 'tour',
            'collection': 'answer'}
    question = ReferenceField(required=True, primary_key=True)
    username = ReferenceField(required=True)
    answer = StringField(required=True)

