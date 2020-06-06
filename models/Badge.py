from mongoengine import *


class Badge(Document):
    """
    Template for a user achievement badge in the Database.
    """
    meta = {'db_alias': 'file',
            'collection': 'badge'}
    # for first set of badges this was set to filename of the picture upon ingestion.
    # can be set in other ways for new badges
    id = StringField(required=True, primary_key=True)
    # was set in the same way as id for the first set. can of course be set independently for new badges
    name = StringField(required=True)
    picture = FileField(content_type='image/png')
    # currently not used in the first set of badges
    description = StringField()
    cost = IntField(required=True)
