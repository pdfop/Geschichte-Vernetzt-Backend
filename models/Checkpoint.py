from mongoengine import *
from models.Tour import Tour


class Checkpoint(Document):
    """
    Parent class for all checkpoints.
    Serves as the most basic checkpoint for texts
    """
    meta = {'db_alias': 'tour',
            'collection': 'checkpoint',
            'allow_inheritance': True}
    tour = ReferenceField(document_type=Tour, reverse_delete_rule=CASCADE)
    text = StringField()
    # TODO: find a way to enforce uniqueness with a reference (tour)
    #       seems rather complicated to do in the model, maybe just enforce it when building the tour
    index = IntField(default=0)
