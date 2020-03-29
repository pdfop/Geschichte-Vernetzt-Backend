from mongoengine import *
from models.Checkpoint import Checkpoint
from models.Picture import Picture


class PictureCheckpoint(Checkpoint):
    """
        A tour Checkpoint containing a Picture.
        Picture and its description are accessed with PictureCheckpoint.picture.picture
            and PictureCheckpoint.picture.description
        Inherits the PictureCheckpoint.description field to allow displaying text
            other than the description of the picture alongside it.
        Currently deprecated as App handles this through the showPictures boolean in the parent checkpoint.
    """
    picture = ReferenceField(document_type=Picture, reverse_delete_rule=CASCADE)
