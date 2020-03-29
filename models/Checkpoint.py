from mongoengine import *
from models.Tour import Tour


class Checkpoint(Document):
    """
    Parent class for all checkpoints. All other checkpoints inherit all fields and may or may not overwrite them.
    Serves as the most basic checkpoint for texts.
    """
    meta = {'db_alias': 'tour',
            'collection': 'checkpoint',
            'allow_inheritance': True}
    tour = ReferenceField(document_type=Tour, reverse_delete_rule=CASCADE)
    text = StringField()
    index = IntField(default=0)
    show_text = BooleanField(default=False)
    show_picture = BooleanField(default=False)
    show_details = BooleanField(default=False)
