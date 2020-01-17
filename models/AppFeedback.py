from mongoengine import *


class AppFeedback(Document):
        """
            Template for an app-feedback object in the Database.
        """
        meta = {'db_alias': 'feedback',
                'collection': 'feedback'}
        rating = IntField(required=True)
        review = StringField(required=True)
        read = BooleanField(default=False)
