from flask_graphql_auth import get_jwt_identity, query_jwt_required
from graphene import ObjectType, List, String, Field, Int
from app.Fields import User, Favourites, Tour, MuseumObject, Answer, TourFeedback, Question, Checkpoint, \
    CheckpointUnion, ProfilePicture
from models.User import User as UserModel
from models.Tour import Tour as TourModel
from models.Answer import Answer as AnswerModel
from models.Favourites import Favourites as FavouritesModel
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.TourFeedback import TourFeedback as TourFeedbackModel
from models.Question import Question as QuestionModel
from models.Checkpoint import Checkpoint as CheckpointModel
from models.ProfilePicture import ProfilePicture as ProfilePictureModel

"""
    These are the queries available to the App API. 
    Included queries: 
        favourite objects 
        favourite tours 
        owned tours 
        all tours the user is a member of 
        a specific tour a user is a member of 
        objects in the database 
        feedback for a specific tour the user owns 
        all answers to a certain question 
        all answers by a certain user 
        all my answers 
        
        
"""


class Query(ObjectType):
    favourite_tours = List(Tour, token=String())
    favourite_objects = List(MuseumObject, token=String())

    @classmethod
    @query_jwt_required
    def resolve_favourite_tours(cls, _, info):
        username = get_jwt_identity()
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            if FavouritesModel.objects(user=user):
                return list(FavouritesModel.objects.get(user=user).favourite_tours)
        return None

    @classmethod
    @query_jwt_required
    def resolve_favourite_objects(cls, _, info):
        username = get_jwt_identity()
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            if FavouritesModel.objects(user=user):
                return list(FavouritesModel.objects.get(user=user).favourite_objects)
        return None

        # queries related to tours

    """Query a specific Tour. Must be a member of the Tour.
       Parameters: token, String, access token of a user
                   tour_id, String, document id of an existing tour the owner of the token is a member of
       if successful returns the Tour
       if unsuccessful because the tour does not exist or the user is not a member of the tour returns Null and False
       if unsuccessful because the toke is invalid returns an empty value for ok
        """
    tour = List(Tour, token=String(), tour_id=String())
    """ Returns all tours a user is a Member of."""
    my_tours = List(Tour, token=String())
    """Returns all tours a user has created."""
    owned_tours = List(Tour, token=String())
    """Returns all feedback submitted for a tour. Can only be queried by the Tour owner."""
    feedback = List(TourFeedback, token=String(), tour_id=String())
    """returns all checkpoints that are part of the tour """
    checkpoints_tour = List(CheckpointUnion, token=String(), tour_id=String())
    """returns a single tour by search_id"""
    tour_search_id = List(String, token=String(), search_id=String())
    """returns a single checkpoint by id"""
    checkpoint_id = List(CheckpointUnion, token=String(), checkpoint_id=String())
    """returns all featured tours"""
    featured = List(Tour, token=String())

    @classmethod
    @query_jwt_required
    def resolve_featured(cls, _, info):
        return list(TourModel.objects(status='featured'))

    @classmethod
    @query_jwt_required
    def resolve_my_tours(cls, _, info):
        username = get_jwt_identity()
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            return list(TourModel.objects(users__contains=user))
        return []

    @classmethod
    @query_jwt_required
    def resolve_tour(cls, _, info, tour_id):
        username = get_jwt_identity()
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            if TourModel.objects(id=tour_id):
                tour = TourModel.objects.get(id=tour_id)
                if user in tour.users:
                    return [tour]
        return []

    @classmethod
    @query_jwt_required
    def resolve_owned_tours(cls, _, info):
        username = get_jwt_identity()
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            return list(TourModel.objects(owner=user))
        return []

    @classmethod
    @query_jwt_required
    def resolve_feedback(cls, _, info, tour_id):
        username = get_jwt_identity()
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            if TourModel.objects(id=tour_id):
                tour = TourModel.objects.get(id=tour_id)
            if tour.owner == user:
                return list(TourFeedbackModel.objects(tour=tour))
        return []

    @classmethod
    @query_jwt_required
    def resolve_checkpoints_tour(cls, _, info, tour_id):
        user = UserModel.objects.get(username=get_jwt_identity())
        if TourModel.objects(id=tour_id):
            tour = TourModel.objects.get(id=tour_id)
            if user in tour.users:
                if CheckpointModel.objects(tour=tour):
                    return list(CheckpointModel.objects(tour=tour))
        return []

    @classmethod
    @query_jwt_required
    def resolve_tour_search_id(cls, _, info, search_id):
        """ NOTE: This only returns the tour id, not the tour object.
        The id can be used in combination with the session id to join the tour. Users that are a member of a tour can
         use the id of the tour to get the tour object which allows for further retrieval of tour fields and checkpoints
         """
        if TourModel.objects(search_id=search_id):
            tour = TourModel.objects.get(search_id=search_id)
            return [tour.id]
        return []

    @classmethod
    @query_jwt_required
    def resolve_checkpoint_id(cls, _, info, checkpoint_id):
        user = UserModel.objects.get(username=get_jwt_identity())
        if CheckpointModel.objects(id=checkpoint_id):
            checkpoint = CheckpointModel.objects.get(id=checkpoint_id)
            tour = checkpoint.tour
            if user == tour.owner:
                return [checkpoint]
        return []

    # master query for objects

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
                         time_range=String(),
                         location=String(),
                         description=String(),
                         interdisciplinary_context=String(),
                         additional_information=String(),
                         size=String())

    @classmethod
    @query_jwt_required
    def resolve_all_objects(cls, _, info):
        return MuseumObjectModel.objects.all()

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

    """ returns the current user as object allowing to query e.g. the profile picture id"""
    me = List(User, token=String())
    """ returns the id of the profile picture of a given username. picture can then be loaded by calling the 
        file/download function with type='ProfilePicture' and id= the id returned by this 
    """
    profile_picture = List(String, token=String(), username=String())
    """ returns the ids of all possible profile pictures """
    available_profile_pictures = List(String, token=String())

    @classmethod
    @query_jwt_required
    def resolve_available_profile_pictures(cls, _, info):
        ids = []
        for pic in ProfilePictureModel.objects.all():
            ids.append(pic.id)
        return ids

    @classmethod
    @query_jwt_required
    def resolve_me(cls, _, info):
        return list(UserModel.objects.get(username=get_jwt_identity()))

    @classmethod
    @query_jwt_required
    def resolve_profile_picture(cls, _, info, username):
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            pic_id = user.profile_picture.id
            return [pic_id]
        return []

