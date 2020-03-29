from flask_graphql_auth import query_jwt_required, get_jwt_claims
from graphene import ObjectType, List, String
from app.Fields import Tour, MuseumObject, Code, AppFeedback, TourFeedback, CheckpointUnion
from models.AppFeedback import AppFeedback as AppFeedbackModel
from models.Tour import Tour as TourModel
from models.Code import Code as CodeModel
from models.TourFeedback import TourFeedback as TourFeedbackModel
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.Checkpoint import Checkpoint as CheckpointModel
from app.WebMutations import admin_claim


class Query(ObjectType):
    """ returns all tours pending for review """
    pending = List(Tour, token=String())
    """ returns all currently featured tours """
    featured = List(Tour, token=String())
    """ returns all feedback ever submitted for the app """
    feedback = List(AppFeedback, token=String())
    """ returns only unread feedback """
    unread_feedback = List(AppFeedback, token=String())
    """ returns all promotion codes currently available in the database"""
    codes = List(Code, token=String())
    """ allows admins to query all feedback for any tour e.g. to assist in the review process"""
    tour_feedback = List(TourFeedback, tour_id=String(), token=String())
    """ allows admins to query any tour """
    tour = List(Tour, token=String(), tour_id=String())
    """ allows admins to query any checkpoint """
    checkpoint = List(CheckpointUnion, token=String(), checkpoint_id=String())
    """ allows admins to query all checkpoints that are part of a given tour """
    checkpoints_by_tour = List(CheckpointUnion, token=String(), tour_id=String())
    """ returns all museum objects currently in the database """
    all_objects = List(MuseumObject, token=String())
    """ returns all objects matching the queryset. all parameters except token are optional. 
        accepts as few or many as needed. in the current iteration all text fields have to be queried using the EXACT 
        value in the database.
    """
    museum_object = List(MuseumObject, object_id=String(),
                         category=String(),
                         sub_category=String(),
                         title=String(),
                         token=String(required=True),
                         year=String(),
                         art_type=String(),
                         creator=String(),
                         material=String(),
                         time_range=String(),
                         location=String(),
                         description=String(),
                         interdisciplinary_context=String(),
                         additional_information=String(),
                         size=String())


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
        location = kwargs.get('location', None)
        description = kwargs.get('description', None)
        interdisciplinary_context = kwargs.get('interdisciplinary_context', None)
        time_range = kwargs.get('time_range', None)
        additional_information = kwargs.get('additional_information', None)
        size = kwargs.get('size', None)

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
            result = result(year=year)
        if art_type is not None:
            result = result(art_type=art_type)
        if creator is not None:
            result = result(creator=creator)
        if material is not None:
            result = result(material=material)
        if time_range is not None:
            result = result(time_range=time_range)
        if location is not None:
            result = result(location=location)
        if description is not None:
            result = result(description=description)
        if interdisciplinary_context is not None:
            result = result(interdisciplinary_context=interdisciplinary_context)
        if additional_information is not None:
            result = result(additional_information=additional_information)
        if size is not None:
            result = result(size_=size)
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

