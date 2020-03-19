from mongoengine import *
from models.MuseumObject import MuseumObject
from models.Checkpoint import Checkpoint


class Question(Checkpoint):
    """
        Parent Class for Question Checkpoints.
        Serves as the most basic model for text questions with text answers as well
        New Question types may be added by subclassing this like class NewType(Question)
        This and all subclasses inherit from Checkpoint meaning they are linked to a Tour and stored in tour.checkpoints
    """
    meta = {'allow_inheritance': True}
    question = StringField(required=True)
    linked_objects = ListField(ReferenceField(document_type=MuseumObject, reverse_delete_rule=PULL))
