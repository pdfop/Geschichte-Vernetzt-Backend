from mongoengine import *
from models.MuseumObject import MuseumObject
from models.Checkpoint import Checkpoint


class ObjectCheckpoint(Checkpoint):
    """
        Wraps a museum object as a checkpoint. Inherits all fields from checkpoint and is thus saved in tour.checkpoint
    """
    museum_object = ReferenceField(document_type=MuseumObject, reverse_delete_rule=CASCADE)
