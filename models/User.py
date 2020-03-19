from mongoengine import *
from models.Badge import Badge
from models.ProfilePicture import ProfilePicture

badge_dict = {}
for badge in Badge.objects.all():
    badge_dict[badge.id] = 0


class User(Document):
    """
        Template for a user in the Database.
    """
    meta = {'db_alias': 'user',
            'collection': 'user'}
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    producer = BooleanField(default=False)
    badges = ListField(ReferenceField(document_type=Badge, reverse_delete_rule=PULL))
    # TODO: possibly add a default picture here. Would have to know document id of the ProfilePicture on the server
    #       to use as default. Seems unsafe to hardcode this if database changes though.
    #       Could maybe also register a new delete rule that resets it to a default picture if the chose one is deleted.
    profile_picture = ReferenceField(document_type=ProfilePicture, reverse_delete_rule=NULLIFY)
    badge_progress = DictField(default=badge_dict)
