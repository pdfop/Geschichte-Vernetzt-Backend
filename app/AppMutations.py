from flask_graphql_auth import create_access_token, create_refresh_token, mutation_jwt_refresh_token_required, \
    get_jwt_identity, mutation_jwt_required
from graphene import ObjectType, List, Mutation, String, Field, Boolean, Int
from werkzeug.security import generate_password_hash, check_password_hash
from .ProtectedFields import ProtectedBool, BooleanField
from app.Fields import User, AppFeedback, Favourites, Tour, Question, Answer, TourFeedback, MuseumObject
from models.User import User as UserModel
from models.Code import Code as CodeModel
from models.Tour import Tour as TourModel
from models.Answer import Answer as AnswerModel
from models.Question import Question as QuestionModel
from models.Favourites import Favourites as FavouritesModel
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.AppFeedback import AppFeedback as AppFeedbackModel
from models.TourFeedback import TourFeedback as TourFeedbackModel

"""
These are the mutations available in the App API. 
Tasks: - account creation 
       - login 
       - account management ( change password, delete account) 
       - manage favourite objects and tours 
       - provide feedback for the app 
       - created tours and questions 
       - set session ids 
       - join tours using the session id 
       - create and submit answers 
       - provide feedback for tours 
       
login returns access and refresh token. all other requests require a valid access token.  
"""


class CreateUser(Mutation):
    """Create a user account.
       Parameters: username, String, name of the account. has to be unique
                   password, String, password, no requirements, saved as a hash
       if successful returns the created user and ok=True
       fails if the username is already taken. returns Null and False in that case
    """
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
    """Use a promotion code to promote a user's account to producer status.
       Parameters: token, String, valid jwt access token of a user
                   code, String, 5 character string used as promotion password
        if successful returns the updated user object and ok=True
        if unsuccessful because the code was invalid returns Null and False
        if unsuccessful because the token was invalid returns empty value for ok
        """
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
            return PromoteUser(ok=BooleanField(boolean=False), user=None)
        else:
            code_doc = CodeModel.objects.get(code=code)
            code_doc.delete()
            user = UserModel.objects.get(username=username)
            user.update(set__producer=True)
            user.save()
            user.reload()
            return PromoteUser(ok=BooleanField(boolean=True), user=user)


class ChangePassword(Mutation):
    """Change a user's password.
       Requires the user to be logged in.
       Parameters: token, String, valid jwt access token of a user
                   password, String, the NEW password
       if successful returns True
       if unsuccessful because the token is invalid returns an empty value
    """
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
    """Login. Create a session and jwt access and refresh tokens.
       Parameters: username, String, the username of the account you wish to log in to
                   password, String, the password of the account. password is hashed and compared to the saved hash.
        if successful returns a jwt accessToken (String), a jwt refresh token (String) and True
        if unsuccessful because the user does not exist or the password was invalid returns Null Null and False"""
    class Arguments:
        username = String(required=True)
        password = String(required=True)

    access_token = String()
    refresh_token = String()
    ok = Boolean()

    @classmethod
    def mutate(cls, _, info, username, password):
        if not (UserModel.objects(username=username) and check_password_hash(
                UserModel.objects.get(username=username).password, password)):
            return Auth(ok=False, access_token=None, refresh_token=None)
        else:

            return Auth(access_token=create_access_token(username), refresh_token=create_refresh_token(username),
                        ok=True)


class Refresh(Mutation):
    """Refresh a user's access token.
       Parameter: refreshToken, String, valid jwt refresh token.
       if successful return a new jwt access token for the owner of the refresh token. this invalidates old access tokens.
       if unsuccessful because the refresh token was invalid returns Null
    """
    class Arguments(object):
        refresh_token = String()

    new_token = String()

    @classmethod
    @mutation_jwt_refresh_token_required
    def mutate(cls, info):
        current_user = get_jwt_identity()
        return Refresh(new_token=create_access_token(identity=current_user))


# TODO: Test for safety, add favourite deletion


class DeleteAccount(Mutation):
    """Delete a user account.
       Deleting an account will also delete any tours, questions, answers and favourites created by this user.
       Parameter: token, String, valid jwt access token of the account to be deleted.
       returns True if successful
       returns Null if token was invalid
       """
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
    """Send Feedback about the App to the admins. Feedback is anonymous.
        Feedback consists of a rating on a scale from 1-5 and a text review.
        Parameters: token, String, valid jwt access token of a user
                    rating, Int, rating on a scale of 1-5
                    review, String, text review / feedback
        returns the feedback object and True if successful
        returns Null and an empty value for ok if the token was invalid """
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
    """Add an object to a user's favourites.
       Parameters: token, String, valid jwt access token of a user
                   objectId, String, inventory ID of the object to be added
       returns the list of favourites and True if successful
       returns Null and False if the object does not exist
       returns Null and an empty value for ok if the token was invalid """
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
    """Remove an object from a user's list of favourite objects.
      Parameters: token, String, valid jwt access token of a user
                   objectId, String, inventory ID of the object to be removed
       returns the updated list of favourites and True if successful
       returns None and False if the user does not have any favourites
       returns None and an empty value for ok if the token is invalid
       This operation works and is successful if the object supplied is not part of the user's favourites or does  not
       even exist.
    """
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
    """Add a tour to a user's list of favourite tours.
      Parameters: token, String, valid jwt access token of a user
                   tourId, String, document ID of the tour to be added
      returns the updated list of favourites and True if successful.
      returns Null and False if the tour does not exits
      returns Null and an empty value for ok is the token is invalid
    """

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
    """Remove a tour to a user's list of favourite tours.
          Parameters: token, String, valid jwt access token of a user
                       tourId, String, document ID of the tour to be removed
          returns the updated list of favourites and True if successful.
          returns None and False if the user does not have any favourites
          returns None and an empty value for ok if the token is invalid
       This operation works and is successful if the tour supplied is not part of the user's favourites or does  not
       even exist.
        """
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


class CreateTour(Mutation):
    """ Create a tour
        Parameters: token, String, jwt access token of a user
                    name, String, name of the tour
                    session_id, Int, passcode used to join the tour
        can only be used by users whose 'producer' attribute is True
        if successful returns the created Tour object and a Boolean True
        if unsuccessful because the owner of the token is not a producer returns Null and False
        if unsuccessful because the token is invalid returns an empty value for ok
    """

    class Arguments:
        token = String(required=True)
        name = String(required=True)
        session_id = Int(required=True)

    tour = Field(lambda: Tour)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, name, session_id):
        owner_name = get_jwt_identity()
        if UserModel.objects(username=owner_name):
            owner = UserModel.objects.get(username=owner_name)
            if owner.producer:
                users = [owner]
                tour = TourModel(owner=owner, name=name, users=users, session_id=session_id)
                tour.save()
                return CreateTour(tour=tour, ok=BooleanField(boolean=True))
            else:
                return CreateTour(tour=None, ok=BooleanField(boolean=False))


class CreateAnswer(Mutation):
    class Arguments:
        token = String(required=True)
        answer = String(required=True)
        question = String(required=True)

    answer = Field(Answer)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, answer, question):
        username = get_jwt_identity()
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            if QuestionModel.objects(id=question):
                question = QuestionModel.objects.get(id=question)
            else:
                return CreateAnswer(answer=None, ok=BooleanField(boolean=False))
            if not AnswerModel.objects(question=question, user=user):
                answer = AnswerModel(question=question, user=user, answer=answer)
                answer.save()
                return CreateAnswer(answer=answer, ok=BooleanField(boolean=True))
            else:
                prev = AnswerModel.objects.get(question=question, user=user)
                prev.update(set__answer=answer)
                prev.reload()
                return CreateAnswer(answer=prev, ok=BooleanField(boolean=True))
        else:
            return CreateAnswer(answer=None, ok=BooleanField(boolean=False))


class CreateQuestion(Mutation):
    class Arguments:
        token = String(required=True)
        linked_objects = List(of_type=String)
        question_text = String(required=True)

    question = Field(Question)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, question_text, linked_objects):
        username = get_jwt_identity()
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            if user.producer:
                question = QuestionModel(linked_objects=linked_objects,
                                         question=question_text)
                question.save()
                return CreateQuestion(question=question,
                                      ok=BooleanField(boolean=True))

            else:
                return CreateQuestion(question=None, ok=BooleanField(boolean=False))


class AddObject(Mutation):
    """Add an object to a tour
       Parameters:  token, String, access token of a user
                    tour_id, String, document id of an existing Tour document in the database, tour has to be created by
                                    the owner of the token
                    object_id, String, museum inventory number of an object that exists in the database
        if successful returns the updated Tour object and a Boolean True
        if unsuccessful because the tour_id or object_id was invalid or because the owner of the token does not own the
            tour returns Null and False
        if unsuccessful because the token was invalid returns an empty value for ok
    """

    class Arguments:
        tour_id = String(required=True)
        object_id = String(required=True)
        token = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id, object_id):
        if TourModel.objects(id=tour_id):
            tour = TourModel.objects.get(id=tour_id)
            if tour.owner.username == get_jwt_identity():
                if MuseumObjectModel.objects(object_id=object_id):
                    museum_object = MuseumObjectModel.objects.get(object_id=object_id)
                    referenced = tour.referenced_objects
                    referenced.append(museum_object)
                    tour.update(set__referenced_objects=referenced)
                    tour.save()
                    tour = TourModel.objects.get(id=tour_id)
                    return AddObject(ok=BooleanField(boolean=True), tour=tour)
                else:
                    return AddObject(ok=BooleanField(boolean=False), tour=None)
            else:
                return AddObject(ok=BooleanField(boolean=False), tour=None)
        else:
            return AddObject(ok=BooleanField(boolean=False), tour=None)


class AddQuestion(Mutation):
    class Arguments:
        tour_id = String(required=True)
        question = String(required=True)
        token = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id, question):
        if TourModel.objects(id=tour_id):
            tour = TourModel.objects.get(id=tour_id)
            if tour.owner.username == get_jwt_identity():
                if QuestionModel.objects(id=question):
                    question = QuestionModel.objects.get(id=question)
                    questions = tour.questions
                    questions.append(question)
                    tour.update(set__questions=questions)
                    tour.save()
                    tour = TourModel.objects.get(id=tour_id)
                    return AddQuestion(ok=BooleanField(boolean=True), tour=tour)
                else:
                    return AddQuestion(ok=BooleanField(boolean=False), tour=None)
            else:
                return AddQuestion(ok=BooleanField(boolean=False), tour=None)
        else:
            return AddQuestion(ok=BooleanField(boolean=False), tour=None)


class AddAnswer(Mutation):
    class Arguments:
        answer_id = String(required=True)
        tour_id = String(required=True)
        question_id = String(required=True)
        token = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id, question_id, answer_id):
        if TourModel.objects(id=tour_id):
            tour = TourModel.objects.get(id=tour_id)
            username = get_jwt_identity()
            if UserModel.objects(username=username):
                user = UserModel.objects.get(username=username)
                if user in tour.users:
                    answers = tour.answers
                    if question_id in answers.keys():
                        answers[question_id].update({user.username: answer_id})
                    else:
                        answers[question_id] = {user.username: answer_id}
                    tour.update(set__answers=answers)
                    tour.save()
                    tour.reload()
                    return AddAnswer(tour=tour, ok=BooleanField(boolean=True))
                else:
                    return AddAnswer(tour=None, ok=BooleanField(boolean=False))
            else:
                return AddAnswer(tour=None, ok=BooleanField(boolean=False))
        else:
            return AddAnswer(tour=None, ok=BooleanField(boolean=False))


class AddMember(Mutation):
    """Join a Tour using it's session code.
       Parameters: token, String, access token of a user
                   tour_id, String, document id of an existing Tour object
                   session_id, Int, current session id of the tour
       if successful returns the Tour object the user joined and a Boolean True
       if unsuccessful because the Tour does not exist or the session code is invalid returns Null and False
       if unsuccessful because the token was invalid returns an empty value for ok
    """

    class Arguments:
        tour_id = String(required=True)
        token = String(required=True)
        session_id = Int(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id, session_id):
        if TourModel.objects(id=tour_id):
            tour = TourModel.objects.get(id=tour_id)
            if tour.session_id == session_id:
                username = get_jwt_identity()
                if UserModel.objects(username=username):
                    user = UserModel.objects.get(username=username)
                    users = tour.users
                    if user not in users:
                        users.append(user)
                        tour.update(set__users=users)
                        tour.save()
                        tour.reload()
                        return AddMember(ok=BooleanField(boolean=True), tour=tour)
                    else:
                        return AddMember(ok=BooleanField(boolean=False), tour=None)
                else:
                    return AddMember(ok=BooleanField(boolean=False), tour=None)
            else:
                return AddMember(ok=BooleanField(boolean=False), tour=None)
        else:
            return AddMember(ok=BooleanField(boolean=False), tour=None)


class SubmitReview(Mutation):
    """Submit a tour for review by the administrators.
    Parameters: token, String, access token of a user, owner must be the creator of the tour
                tour_id, String, document id of an existing Tour
    if successful returns the Tour object and a Boolean True
    if unsuccessful because the Tour does not exist or the token does not belong to the owner of
        the tour returns Null and False
    if unsuccessful because the token was invalid returns an empty value for ok
    """

    class Arguments:
        tour_id = String(required=True)
        token = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id):
        if TourModel.objects(id=tour_id):
            tour = TourModel.objects.get(id=tour_id)
            username = get_jwt_identity()
            if tour.owner.username == username:
                tour.update(set__status='pending')
                tour.save()
                tour.reload()
                return SubmitReview(ok=BooleanField(boolean=True), tour=tour)
            else:
                return SubmitReview(ok=BooleanField(boolean=False), tour=None)
        else:
            return SubmitReview(ok=BooleanField(boolean=False), tour=None)


class UpdateSessionId(Mutation):
    """Change the session id of a tour.
       Parameters: token, String, access token of a user, owner must be the owner of the tour
                   tour, String, document id of an existing Tour owned by the owner of the token
                   session_id, Int, value the session id should be updated to
       if successful returns the Tour and a Boolean True
       if unsuccessful because the Tour does not exist or the token does not belong to the owner of the tour
            returns Null and False
       if unsuccessful because the token was invalid returns an empty value for ok
       """

    class Arguments:
        token = String(required=True)
        tour = String(required=True)
        session_id = Int(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour, session_id):
        if TourModel.objects(id=tour):
            tour = TourModel.objects.get(id=tour)
            username = get_jwt_identity()
            if tour.owner.username == username:
                tour.update(set__session_id=session_id)
                tour.save()
                tour.reload()
                return UpdateSessionId(tour=tour, ok=BooleanField(boolean=True))
            else:
                return UpdateSessionId(tour=None, ok=BooleanField(boolean=False))
        else:
            return UpdateSessionId(tour=None, ok=BooleanField(boolean=False))


class RemoveMuseumObject(Mutation):
    """Remove an Object from a Tour.
       Parameters: token, String, access token of a user, owner must be the creator of the tour
                   tour_id, String, document id of an existing Tour
                   object_id, String, museum inventory number of the object to be removed
        if successful returns the updated Tour object and a Boolean True
            note this operation is successful if the object was already not referenced in the tour
        if unsuccessful because the Tour does not exist or the token does not belong to the owner of
            the tour or the object does not exist returns Null and False
        if unsuccessful because the token was invalid returns an empty value for ok
    """

    class Arguments:
        token = String(required=True)
        tour = String(required=True)
        object_id = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour, object_id):
        if TourModel.objects(id=tour):
            tour = TourModel.objects.get(id=tour)
            username = get_jwt_identity()
            if tour.owner.username == username:
                if MuseumObjectModel.objects(object_id=object_id):
                    museum_object = MuseumObjectModel.objects.get(object_id=object_id)
                    referenced = tour.referenced_objects
                    if museum_object in referenced:
                        referenced.remove(museum_object)
                    tour.update(set__referenced_objects=referenced)
                    tour.save()
                    tour.reload()
                    return RemoveMuseumObject(tour=tour, ok=BooleanField(boolean=True))
                else:
                    return RemoveMuseumObject(tour=None, ok=BooleanField(boolean=False))
            else:
                return RemoveMuseumObject(tour=None, ok=BooleanField(boolean=False))
        else:
            return RemoveMuseumObject(tour=None, ok=BooleanField(boolean=False))


class RemoveQuestion(Mutation):
    """Remove a Question from a Tour.
       Parameters: token, String, access token of a user, owner must be the creator of the tour
                   tour_id, String, document id of an existing Tour
                   question_id, String, document id of the question to be removed
       if successful returns the Tour object and a Boolean True
            note this operation is successful if the question was already not referenced in the tour
        if unsuccessful because the Tour does not exist or the token does not belong to the owner of
            the tour or the question does not exist returns Null and False
        if unsuccessful because the token was invalid returns an empty value for ok
    """

    class Arguments:
        token = String(required=True)
        tour_id = String(required=True)
        question_id = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id, question_id):
        if TourModel.objects(id=tour_id):
            tour = TourModel.objects.get(id=tour_id)
            username = get_jwt_identity()
            if tour.owner.username == username:
                if QuestionModel.objects(id=question_id):
                    question = QuestionModel.objects.get(id=question_id)
                    questions = tour.questions
                    if question in questions:
                        questions.remove(question)
                        question.delete()
                    tour.update(set__questions=questions)
                    tour.save()
                    tour.reload()
                    answers = tour.answers
                    for answer in answers:
                        if answer.question == question:
                            answers.remove(answer)
                            answer.delete()
                            tour.update(set__answers=answers)
                    tour.save()
                    tour.reload()
                    return RemoveQuestion(tour=tour, ok=BooleanField(boolean=True))
                else:
                    return RemoveQuestion(tour=None, ok=BooleanField(boolean=False))
            else:
                return RemoveQuestion(tour=None, ok=BooleanField(boolean=False))
        else:
            return RemoveQuestion(tour=None, ok=BooleanField(boolean=False))


class RemoveUser(Mutation):
    class Arguments:
        """Kick a user from a Tour.
        Parameters: token, String, access token of a user, owner must be the creator of the tour
                   tour_id, String, document id of an existing Tour
                   username, String, name of the user to be removed
        if successful returns the updated Tour object and a Boolean True
            note this operation is successful if the user was already not part of the tour
        if unsuccessful because the Tour does not exist or the token does not belong to the owner of
            the tour or the username does not exist returns Null and False
        if unsuccessful because the token was invalid returns an empty value for ok

        """
        token = String(required=True)
        tour_id = String(required=True)
        username = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id, username):
        if TourModel.objects(id=tour_id):
            tour = TourModel.objects.get(id=tour_id)
            owner = get_jwt_identity()
            if tour.owner.username == owner:
                if UserModel.objects(username=username):
                    user = UserModel.objects.get(username=username)
                    users = tour.users
                    if user in users:
                        users.remove(user)
                    tour.update(set__users=users)
                    tour.save()
                    tour.reload()
                    return RemoveUser(tour=tour, ok=BooleanField(boolean=True))
                else:
                    return RemoveUser(tour=None, ok=BooleanField(boolean=False))
            else:
                return RemoveUser(tour=None, ok=BooleanField(boolean=False))
        else:
            return RemoveUser(tour=None, ok=BooleanField(boolean=False))


class SubmitFeedback(Mutation):
    """Submit feedback for a Tour.
    Parameters: token, String, access token of a user
                   tour_id, String, document id of an existing Tour
                   rating, Int, rating on a scale of 1-5
                   review, String, text review for the tour
        Feedback is anonymous i.e. the user is submitting the feedback is not logged
        Also note that a user has to be part of a tour in order to submit feedback about it
        if successful returns the Feedback object and a Boolean True
        if unsuccessful because the Tour does not exist or the user does not exits or is not a member of the tour
            or the rating value is invalid returns Null and False
        if unsuccessful because the token was invalid returns an empty value for ok """

    class Arguments:
        tour_id = String(required=True)
        token = String(required=True)
        rating = Int(required=True)
        review = String(required=True)

    ok = Field(ProtectedBool)
    feedback = Field(TourFeedback)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, rating, tour_id, review):
        if TourModel.objects(id=tour_id):
            tour = TourModel.objects.get(id=tour_id)
            if UserModel.objects(username=get_jwt_identity()):
                user = UserModel.objects.get(username=get_jwt_identity())
                if user in tour.users:
                    if rating in range(1, 6):
                        feedback = TourFeedbackModel(rating=rating, review=review, tour=tour)
                        feedback.save()
                        return SubmitFeedback(ok=BooleanField(boolean=True), feedback=feedback)
                    else:
                        return SubmitFeedback(ok=BooleanField(boolean=False), feedback=None)
                else:
                    return SubmitFeedback(ok=BooleanField(boolean=False), feedback=None)
            else:
                return SubmitFeedback(ok=BooleanField(boolean=False), feedback=None)
        else:
            return SubmitFeedback(ok=BooleanField(boolean=False), feedback=None)


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
    app_feedback = SendFeedback.Field()
    create_tour = CreateTour.Field()
    create_question = CreateQuestion.Field()
    create_answer = CreateAnswer.Field()
    add_question = AddQuestion.Field()
    add_answer = AddAnswer.Field()
    add_object = AddObject.Field()
    add_member = AddMember.Field()
    submit_for_review = SubmitReview.Field()
    update_session_id = UpdateSessionId.Field()
    remove_museum_object = RemoveMuseumObject.Field()
    remove_question = RemoveQuestion.Field()
    remove_user = RemoveUser.Field()
    submit_tour_feedback = SubmitFeedback.Field()
