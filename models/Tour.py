from mongoengine import *


class Tour(Document):
    """
    Template for a tour in the Database.
    """
    meta = {'db_alias': 'tour',
            'collection': 'tour'}
    id = IntField(required=True, primary_key=True)
    name = StringField(required=True)
    owner = ReferenceField(required=True)
    referenced_objects = ListField()
    questions = ListField()
    answers = DictField()
    users = ListField()


