import datetime
from mongoengine import *
from models.User import User


class Tour(Document):
    """
    Template for a tour in the Database.
    """
    meta = {'db_alias': 'tour',
            'collection': 'tour'}
    name = StringField(required=True)
    owner = ReferenceField(document_type=User, required=True, reverse_delete_rule=CASCADE)
    search_id = StringField(required=True, unique=True)
    session_id = IntField(required=True)
    users = ListField(ReferenceField(document_type=User, reverse_delete_rule=PULL))
    status = StringField(default='private')
    difficulty = IntField(required=True, min_value=1, max_value=5)
    description = StringField()
    creation = DateTimeField(default=datetime.datetime.utcnow)
    current_checkpoints = IntField(default=0)
