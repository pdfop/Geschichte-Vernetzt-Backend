from flask_graphql_auth import get_jwt_identity, query_jwt_required
from graphene import ObjectType, List, String, Field
from app.Fields import User, Favourites, Tour, MuseumObject, Answer, TourFeedback, Question
from models.User import User as UserModel
from models.Tour import Tour as TourModel
from models.Answer import Answer as AnswerModel
from models.Favourites import Favourites as FavouritesModel
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.TourFeedback import TourFeedback as TourFeedbackModel
from models.Question import Question as QuestionModel


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
        user = UserModel.objects.get(username=get_jwt_identity())
        if FavouritesModel.objects(user=user):
            return list(FavouritesModel.objects.get(user=user).favourite_tours)
        else:
            return None

    @classmethod
    @query_jwt_required
    def resolve_favourite_objects(cls, _, info):
        user = UserModel.objects.get(username=get_jwt_identity())
        if FavouritesModel.objects(user=user):
            return list(FavouritesModel.objects.get(user=user).favourite_objects)
        else:
            return None

        # queries related to tours

    """Query a specific Tour. Must be a member of the Tour.
       Parameters: token, String, access token of a user
                   tour_id, String, document id of an existing tour the owner of the token is a member of
       if successful returns the Tour
       if unsuccessful because the tour does not exist or the user is not a member of the tour returns Null and False
       if unsuccessful because the toke is invalid returns an empty value for ok
        """
    tour = List(Tour, token=String(), tour=String())
    """ Returns all tours a user is a Member of."""
    my_tours = List(Tour, token=String())
    """Returns all tours a user has created."""
    owned_tours = List(Tour, token=String())
    """Returns all feedback submitted for a tour. Can only be queried by the Tour owner."""
    feedback = List(TourFeedback, token=String(), tour=String())

    @classmethod
    @query_jwt_required
    def resolve_my_tours(cls, _, info):
        username = get_jwt_identity()
        user = UserModel.objects.get(username=username)
        return list(TourModel.objects(users__contains=user))

    @classmethod
    @query_jwt_required
    def resolve_tour(cls, _, info, tour):
        username = get_jwt_identity()
        user = UserModel.objects.get(username=username)
        tour = TourModel.objects.get(id=tour)
        if user in tour.users:
            return [tour]
        else:
            return []

    @classmethod
    @query_jwt_required
    def resolve_owned_tours(cls, _, info):
        username = get_jwt_identity()
        user = UserModel.objects.get(username=username)
        return list(TourModel.objects(owner=user))

    @classmethod
    @query_jwt_required
    def resolve_feedback(cls, _, info, tour):
        user = UserModel.objects.get(username=get_jwt_identity())
        if TourModel.objects(id=tour):
            tour = TourModel.objects.get(id=tour)
        if tour.owner == user:
            return list(TourFeedbackModel.objects(tour=tour))
        else:
            return []

    # queries related to questions and answers
    answers_to_question = List(Question, token=String(), question=String())
    answers_by_user = List(Answer, tour=String(), token=String(), user=String())
    my_answers = List(Answer, token=String(), tour=String())

    @classmethod
    @query_jwt_required
    def resolve_answers_to_question(cls, _, info, question):
        if QuestionModel.objects(id=question):
            question = QuestionModel.objects.get(id=question)
            return list(AnswerModel.objects(question=question))
        else:
            return None

    # TODO: when adding public and private answers gate private answers to the tour owner

    @classmethod
    @query_jwt_required
    def resolve_answers_by_user(cls, _, info, username, tour):
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            if TourModel.objects(id=tour):
                tour = TourModel.objects.get(id=tour)
                answers = []
                for answer in tour.answers:
                    if answer.user == user:
                        answers.append(answer)
                return answers
        return None

    @classmethod
    @query_jwt_required
    def resolve_my_answers(cls, _, info, tour):
        if TourModel.objects(id=tour):
            tour = TourModel.objects.get(id=tour)
            user = UserModel.objects.get(username=get_jwt_identity())
            answers = []
            for answer in tour.answers:
                if answer.user == user:
                    answers.append(answer)
            return answers
        return None

    # master query for objects
    museum_object = List(MuseumObject, object_id=String(),
                         category=String(),
                         sub_category=String(),
                         title=String(),
                         token=String(required=True),
                         year=String(),
                         picture=String(),
                         art_type=String(),
                         creator=String(),
                         material=String(),
                         size=String(),
                         location=String(),
                         description=String(),
                         interdisciplinary_context=String())

    @classmethod
    @query_jwt_required
    def revolve_museum_object(cls, _, info, **kwargs):
        object_id = kwargs.get('object_id', None)
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        title = kwargs.get('title', None)
        year = kwargs.get('year', None)
        picture = kwargs.get('picture', None)
        art_type = kwargs.get('art_type', None)
        creator = kwargs.get('creator', None)
        material = kwargs.get('material', None)
        size = kwargs.get('size', None)
        location = kwargs.get('location', None)
        description = kwargs.get('description', None)
        interdisciplinary_context = kwargs.get('interdisciplinary_context', None)
        attributes = [object_id, category, sub_category, title, year, picture, art_type, creator, material, size,
                      location, description, interdisciplinary_context]
        names = ["object_id", "category", "sub_category", "title", "year", "picture", "art_type", "creator", "material",
                 "size", "location", "description", "interdisciplinary_context"]
        qs = {}
        print("no")
        for i in range(len(names)):
            if attributes[i] is not None:
                print(names[i])
                qs[names[i]] = attributes[i]
        museum_object = MuseumObjectModel.objects(__raw__=qs)
        return list(museum_object)
