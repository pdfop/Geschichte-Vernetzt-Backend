from flask_graphql_auth import create_access_token, create_refresh_token, mutation_jwt_refresh_token_required, \
    get_jwt_identity, mutation_jwt_required, query_jwt_required
from graphene import ObjectType, Schema, List, Mutation, String, Field, Boolean, Int
from werkzeug.security import generate_password_hash, check_password_hash
from .ProtectedFields import ProtectedBool, BooleanField
from app.Fields import User, AppFeedback, Favourites, Tour, MuseumObject
from models.User import User as UserModel
from models.Code import Code as CodeModel
from models.Tour import Tour as TourModel
from models.Answer import Answer as AnswerModel
from models.Favourites import Favourites as FavouritesModel
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.AppFeedback import AppFeedback as AppFeedbackModel

"""
GraphQL Schema for user management. 
Tasks: - account creation 
       - login 
       - account management ( change password, delete account) 
       - manage favourite objects and tours 
       - provide feedback for the app 
login returns access and refresh token. all other requests require a valid access token.  
"""


class CreateUser(Mutation):
    class Arguments:
        username = String(required=True)
        password = String(required=True)

    user = Field(lambda: User)
    ok = Boolean()

    def mutate(self, info, username, password):
        if not UserModel.objects(username=username):
            user = UserModel(username=username, password=generate_password_hash(password))
            user.save()
            return CreateUser(user=user, ok=True)
        else:
            return CreateUser(user=None, ok=False)


class PromoteUser(Mutation):
    class Arguments:
        token = String()
        code = String()

    ok = Field(ProtectedBool)
    user = Field(User)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, code):
        username = get_jwt_identity()
        if not CodeModel.objects(code=code):
            return PromoteUser(ok=BooleanField(boolean=False))
        else:
            code_doc = CodeModel.objects.get(code=code)
            code_doc.delete()
            user = UserModel.objects.get(username=username)
            user.update(set__producer=True)
            user.save()
            user = UserModel.objects.get(username=username)
            return PromoteUser(ok=BooleanField(boolean=True), user=user)


class ChangePassword(Mutation):
    class Arguments:
        token = String()
        password = String()

    ok = Field(ProtectedBool)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, password):
        username = get_jwt_identity()
        user = UserModel.objects(username=username)[0]
        user.update(set__password=generate_password_hash(password))
        user.save()
        return ChangePassword(ok=BooleanField(boolean=True))


class Auth(Mutation):
    class Arguments:
        username = String(required=True)
        password = String(required=True)

    access_token = String()
    refresh_token = String()
    ok = Boolean()

    @classmethod
    def mutate(cls, _, info, username, password):
        if not (UserModel.objects(username=username) and check_password_hash(
                UserModel.objects(username=username)[0].password, password)):
            return Auth(ok=False)
        else:

            return Auth(access_token=create_access_token(username), refresh_token=create_refresh_token(username),
                        ok=True)


class Refresh(Mutation):
    class Arguments(object):
        refresh_token = String()

    new_token = String()

    @classmethod
    @mutation_jwt_refresh_token_required
    def mutate(cls, info):
        current_user = get_jwt_identity()
        return Refresh(new_token=create_access_token(identity=current_user))


class DeleteAccount(Mutation):
    class Arguments:
        token = String(required=True)

    ok = Field(ProtectedBool)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info):
        username = get_jwt_identity()
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            tours = TourModel.objects(owner=user)
            for tour in tours:
                for question in tour.questions:
                    question.delete()
                for answer in tour.answers:
                    answer.delete()
                tour.delete()
            answers = AnswerModel.objects(owner=user)
            for answer in answers:
                answer.delete()
            user.delete()
        return DeleteAccount(ok=BooleanField(boolean=True))


class SendFeedback(Mutation):
    class Arguments:
        token = String(required=True)
        review = String(required=True)
        rating = Int(required=True)

    ok = Field(ProtectedBool)
    feedback = Field(AppFeedback)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, review, rating):
        feedback = AppFeedbackModel(review=review, rating=rating)
        feedback.save()
        return SendFeedback(ok=BooleanField(boolean=True), feedback=feedback)


class AddFavouriteObject(Mutation):
    class Arguments:
        token = String(required=True)
        object_id = String(required=True)

    ok = Field(ProtectedBool)
    favourites = Field(Favourites)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, object_id):
        user = UserModel.objects.get(username=get_jwt_identity())
        if MuseumObjectModel.objects(object_id=object_id):
            museum_object = MuseumObjectModel.objects.get(object_id=object_id)
            if FavouritesModel.objects(user=user):
                favourites = FavouritesModel.object.get(user=user)
                if favourites.favourite_objects:
                    objects = favourites.favourite_objects
                    if museum_object not in objects:
                        objects.append(museum_object)
                        favourites.update(set__favourite_objects=objects)
                        favourites.save()
                else:
                    objects = [museum_object]
                    favourites.update(set__favourite_objects=objects)
                    favourites.save()
                favourites.reload()
                return AddFavouriteObject(ok=BooleanField(boolean=True), favourites=favourites)
            else:
                objects = [museum_object]
                favourites = FavouritesModel(user=user, favourite_objects=objects)
                favourites.save()
                return AddFavouriteObject(ok=BooleanField(boolean=True), favourites=favourites)
        else:
            return AddFavouriteObject(ok=BooleanField(boolean=False), favourites=None)


class RemoveFavouriteObject(Mutation):
    class Arguments:
        token = String(required=True)
        object_id = String(required=True)

    ok = Field(ProtectedBool)
    favourites = Field(Favourites)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, object_id):
        user = UserModel.objects.get(username=get_jwt_identity())
        if FavouritesModel.objects.get(user=user):
            favourites = FavouritesModel.objects.get(user=user)
            if MuseumObjectModel.objects(object_id=object_id):
                museum_object = MuseumObjectModel.objects.get(object_id=object_id)
                if museum_object in favourites.favourite_objects:
                    objects = favourites.favourite_objects
                    objects.remove(museum_object)
                    favourites.update(set__favourite_objects=objects)
                    favourites.save()
                    favourites.reload()
                return RemoveFavouriteObject(ok=BooleanField(boolean=True), favourites=favourites)
        return RemoveFavouriteObject(ok=BooleanField(boolean=False), favourites=None)


class AddFavouriteTour(Mutation):
    class Arguments:
        token = String(required=True)
        tour_id = String(required=True)

    ok = Field(ProtectedBool)
    favourites = Field(Favourites)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id):
        user = UserModel.objects.get(username=get_jwt_identity())
        if TourModel.objects(id=tour_id):
            tour = TourModel.objects.get(id=tour_id)
            if FavouritesModel.objects(user=user):
                favourites = FavouritesModel.objects.get(user=user)
                if favourites.favourite_tours:
                    tours = favourites.favourite_tours
                    if tour not in tours:
                        tours.append(tour)
                        favourites.update(set__favourite_tours=tours)
                        favourites.save()
                else:
                    tours = [tour]
                    favourites.update(set__favourite_tours=tours)
                    favourites.save()
                favourites.reload()
                return AddFavouriteTour(ok=BooleanField(boolean=True), favourites=favourites)
            else:
                tours = [tour]
                favourites = FavouritesModel(user=user, favourite_tours=tours)
                favourites.save()
                return AddFavouriteTour(ok=BooleanField(boolean=True), favourites=favourites)
        else:
            return AddFavouriteTour(ok=BooleanField(boolean=False), favourites=None)


class RemoveFavouriteTour(Mutation):
    class Arguments:
        token = String(required=True)
        tour_id = String(required=True)

    ok = Field(ProtectedBool)
    favourites = Field(Favourites)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id):
        user = UserModel.objects.get(username=get_jwt_identity())
        if FavouritesModel.objects.get(user=user):
            favourites = FavouritesModel.objects.get(user=user)
            if TourModel.objects(id=tour_id):
                tour = TourModel.objects.get(id=tour_id)
                if tour in favourites.favourite_tours:
                    tours = favourites.favourite_tours
                    tours.remove(tour)
                    favourites.update(set__favourite_tours=tours)
                    favourites.save()
                    favourites.reload()
                return RemoveFavouriteTour(ok=BooleanField(boolean=True), favourites=favourites)
        return RemoveFavouriteTour(ok=BooleanField(boolean=False), favourites=None)


class Mutation(ObjectType):
    create_user = CreateUser.Field()
    auth = Auth.Field()
    refresh = Refresh.Field()
    change_password = ChangePassword.Field()
    promote_user = PromoteUser.Field()
    delete_account = DeleteAccount.Field()
    add_favourite_tour = AddFavouriteTour.Field()
    remove_favourite_tour = RemoveFavouriteTour.Field()
    add_favourite_object = AddFavouriteObject.Field()
    remove_favourite_object = RemoveFavouriteObject.Field()
    feedback = SendFeedback.Field()


class Query(ObjectType):
    user = List(User, username=String())

    @classmethod
    def resolve_user(cls, _, info, username):
        return list(UserModel.objects(username=username))

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


user_schema = Schema(query=Query, mutation=Mutation)
