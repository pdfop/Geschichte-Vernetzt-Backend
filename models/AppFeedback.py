from mongoengine import *


class AppFeedback(Document):
    """
          Template for an app-feedback object in the Database.
    """
    meta = {'db_alias': 'feedback',
            'collection': 'feedback'}
    # scale is also enforced upon creation
    rating = IntField(required=True, min_value=1, max_value=5)
    review = StringField(required=True)
    # allows admins to mark this as read and remove it from a 'unread feedback' query
    read = BooleanField(default=False)
