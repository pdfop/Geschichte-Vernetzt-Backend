from graphene import ObjectType, List, String, Field, Boolean, Int
from app.Fields import Tour, MuseumObject, Admin, User, Code, AppFeedback
from models.AppFeedback import AppFeedback as AppFeedbackModel
from models.Tour import Tour as TourModel
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.Admin import Admin as AdminModel


class Query(ObjectType):
    users = List(Admin)
    user = List(Admin, username=String())
    objects = List(MuseumObject, object_id=String())
    pending = List(Tour)
    featured = List(Tour)
    feedback = List(AppFeedback)
    unread_feedback = List(AppFeedback)

    def resolve_feedback(self, info):
        return list(AppFeedbackModel.objects.all())

    def resolve_unread_feedback(self, info):
        return list(AppFeedbackModel.object(read=False))

    def resolve_featured(self, info):
        return list(TourModel.objects(status='featured'))

    def resolve_pending(self, info):
        return list(TourModel.objects(status='pending'))

    def resolve_objects(self, info, object_id):
        return MuseumObjectModel.objects(object_id=object_id)

    def resolve_user(self, info, username):
        return list(AdminModel.objects(username=username))

    def resolve_users(self, info):
        return list(AdminModel.objects.all())