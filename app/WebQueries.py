from flask_graphql_auth import query_jwt_required, get_jwt_claims
from graphene import ObjectType, List, String, Field, Boolean, Int
from app.Fields import Tour, MuseumObject, Code, AppFeedback, TourFeedback, Checkpoint, CheckpointUnion
from models.AppFeedback import AppFeedback as AppFeedbackModel
from models.Tour import Tour as TourModel
from models.Code import Code as CodeModel
from models.TourFeedback import TourFeedback as TourFeedbackModel
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.Checkpoint import Checkpoint as CheckpointModel
from app.WebMutations import admin_claim


class Query(ObjectType):
    pending = List(Tour, token=String())
    featured = List(Tour, token=String())
    feedback = List(AppFeedback, token=String())
    unread_feedback = List(AppFeedback, token=String())
    codes = List(Code, token=String())
    tour_feedback = List(TourFeedback, tour_id=String(), token=String())
    tour = List(Tour, token=String(), tour_id=String())
    checkpoint = List(CheckpointUnion, token=String(), checkpoint_id=String())
    checkpoints_by_tour = List(CheckpointUnion, token=String(), tour_id=String())
    all_objects = List(MuseumObject, token=String())
    museum_object = List(MuseumObject, object_id=String(),
                         category=String(),
                         sub_category=String(),
                         title=String(),
                         token=String(required=True),
                         year=String(),
                         art_type=String(),
                         creator=String(),
                         material=String(),
                         size=String(),
                         location=String(),
                         description=String(),
                         interdisciplinary_context=String())

    @classmethod
    @query_jwt_required
    def resolve_codes(cls, _, info):
        if get_jwt_claims() == admin_claim:
            return list(CodeModel.objects.all())
        else:
            return []

    @classmethod
    @query_jwt_required
    def resolve_tour_feedback(cls, _, info, tour_id):
        if get_jwt_claims() == admin_claim:
            if TourModel.objects(id=tour_id):
                tour = TourModel.objects.get(id=tour_id)
                if TourFeedbackModel.objects(tour=tour):
                    return list(TourFeedbackModel.objects(tour=tour))
        return []

    @classmethod
    @query_jwt_required
    def resolve_feedback(cls, _, info):
        if get_jwt_claims() == admin_claim:
            return list(AppFeedbackModel.objects.all())
        else:
            return []

    @classmethod
    @query_jwt_required
    def resolve_unread_feedback(cls, _, info):
        if get_jwt_claims() == admin_claim:
            return list(AppFeedbackModel.objects(read=False))
        else:
            return []

    @classmethod
    @query_jwt_required
    def resolve_featured(cls, _, info):
        if get_jwt_claims() == admin_claim:
            return list(TourModel.objects(status='featured'))
        else:
            return []

    @classmethod
    @query_jwt_required
    def resolve_pending(cls, _, info):
        if get_jwt_claims() == admin_claim:
            return list(TourModel.objects(status='pending'))
        else:
            return []

    @classmethod
    @query_jwt_required
    def resolve_tour(cls, _, info, tour_id):
        if get_jwt_claims() == admin_claim:
            if TourModel.objects(id=tour_id):
                return list(TourModel.objects(id=tour_id))
        return []

    @classmethod
    @query_jwt_required
    def resolve_museum_object(cls, _, info, **kwargs):
        object_id = kwargs.get('object_id', None)
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        title = kwargs.get('title', None)
        year = kwargs.get('year', None)
        art_type = kwargs.get('art_type', None)
        creator = kwargs.get('creator', None)
        material = kwargs.get('material', None)
        size = kwargs.get('size', None)
        location = kwargs.get('location', None)
        description = kwargs.get('description', None)
        interdisciplinary_context = kwargs.get('interdisciplinary_context', None)
        result = MuseumObjectModel.objects.all()
        if object_id is not None:
            result = result(object_id=object_id)
        if category is not None:
            result = result(category=category)
        if sub_category is not None:
            result = result(sub_category=sub_category)
        if title is not None:
            result = result(title=title)
        if year is not None:
            result = result(year__contains=year)
        if art_type is not None:
            result = result(art_type__contains=art_type)
        if creator is not None:
            result = result(creator__contains=creator)
        if material is not None:
            result = result(material__contains=material)
        if size is not None:
            result = result(size=size)
        if location is not None:
            result = result(location__contains=location)
        if description is not None:
            result = result(description=description)
        if interdisciplinary_context is not None:
            result = result(interdisciplinary_context=interdisciplinary_context)
        return list(result)

    @classmethod
    @query_jwt_required
    def resolve_checkpoint(cls, _,  info, checkpoint_id):
        if get_jwt_claims() == admin_claim:
            if CheckpointModel.objects(id=checkpoint_id):
                return list(CheckpointModel.objects(id=checkpoint_id))
        return []

    @classmethod
    @query_jwt_required
    def resolve_checkpoints_by_tour(cls, _, info, tour_id):
        if get_jwt_claims() == admin_claim:
            if TourModel.objects(id=tour_id):
                tour = TourModel.objects.get(id=tour_id)
                if CheckpointModel.objects(tour=tour):
                    return list(CheckpointModel.objects(tour=tour))
        return []

    @classmethod
    @query_jwt_required
    def resolve_all_objects(cls, _, info):
        return MuseumObjectModel.objects.all()
