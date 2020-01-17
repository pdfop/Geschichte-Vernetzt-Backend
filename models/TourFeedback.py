from mongoengine import *
from models.Tour import Tour


class TourFeedback(Document):
        """
            Template for a tour-feedback object in the Database.
        """
        meta = {'db_alias': 'tour',
                'collection': 'feedback'}
        tour = ReferenceField(document_type=Tour)
        rating = IntField(required=True)
        review = StringField(required=True)
