from flask_graphql_auth import create_access_token, create_refresh_token, mutation_jwt_refresh_token_required, \
    get_jwt_identity, mutation_jwt_required, get_jwt_claims
from graphene import ObjectType, Schema, List, Mutation, String, Field, Boolean, Int
from werkzeug.security import generate_password_hash, check_password_hash
from models.Admin import Admin as AdminModel
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.Code import Code as CodeModel
from models.User import User as UserModel
from models.Tour import Tour as TourModel
from models.Question import Question as QuestionModel
from models.AppFeedback import AppFeedback as AppFeedbackModel
from models.Answer import Answer as AnswerModel
from models.Favourites import Favourites as FavouritesModel
from models.Badge import Badge as BadgeModel
from models.Picture import Picture as PictureModel
from models.ProfilePicture import ProfilePicture as ProfilePictureModel
from models.Checkpoint import Checkpoint as CheckpointModel
from models.PictureCheckpoint import PictureCheckpoint as PictureCheckpointModel
from models.ObjectCheckpoint import ObjectCheckpoint as ObjectCheckpointModel
from models.MultipleChoiceQuestion import MultipleChoiceQuestion as MCQuestionModel
from models.MultipleChoiceAnswer import MultipleChoiceAnswer as MCAnswerModel
from graphene_file_upload.scalars import Upload
import string
import random
from app.ProtectedFields import StringField, ProtectedString, BooleanField, ProtectedBool
from app.Fields import Tour, MuseumObject, Admin, User, Picture, Badge, Checkpoint, PictureCheckpoint, \
    ObjectCheckpoint, Question, MCAnswer, Answer, MCQuestion, CheckpointUnion

"""
These are the mutations available in the web portal 
Tasks: create and manage admin accounts 
       create producer promotion codes 
       demote users 
       delete accounts  
       create and manage the museum objects  
       review tours that have been submitted by producers 
       manage featured tours 
       read app feedback 
        
login creates a jwt access and refresh token. 
most other methods require a valid token

"""

# a user claim that is inserted into the claims of admin access tokens upon creation.
# mutations in this Schema validate that the token includes this claim to ensure functions are only called by admins
admin_claim = {'admin': True}


class CreateMuseumObject(Mutation):
    """ Create a Museum Object.
        Parameters: token, String, required, valid jwt access token with the admin claim
                    objectId, String, required, inventory id of the object in the museum
                    category, String, required, category of the object in the museum. 'Abteilung'
                    subCategory, String, required, sub-category of the object in the museum. 'Sammlungsbereich'
                    title, String, required, name of the object
                    year, List of Strings, optional, year the object was created/found
                    picture, List of Upload, optional,  images in png format
                    art_type, List of Strings, optional, classification of the object e.g. 'painting'
                    creator, List of Strings, optional, creators of the object
                    material, List of Strings, optional, materials the object is made of
                    width, Int, optional, width of the object in centimeters
                    height, Int, optional, height of the object in centimeters
                    length, Int, optional, length of the object in centimeters
                    diameter, optional, Int, diameter of the object in centimeters
                    location, optional, List of Strings, optional, locations the object was made/found at
                    description, String, optional, description of the object
                    additionalInformation, String, optional, any additional information about the object
                    interdisciplinary_context, List of String, optional, interdisciplinary relations of the object
        returns the object and True if successful
        returns Null and False if token did not belong to admin or object with that id already existed
        returns Null and an empty value for ok if token was invalid """

    class Arguments:
        object_id = String(required=True)
        category = String(required=True)
        sub_category = String(required=True)
        title = String(required=True)
        token = String(required=True)
        time_range = String()
        year = List(String)
        picture = List(Upload)
        art_type = List(String)
        creator = List(String)
        material = List(String)
        width = Int()
        height = Int()
        length = Int()
        diameter = Int()
        location = List(String)
        description = String()
        additional_information = String()
        interdisciplinary_context = List(String)

    museum_object = Field(lambda: MuseumObject)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, object_id, category, sub_category, title, **kwargs):
        year = kwargs.get('year', None)
        picture = kwargs.get('picture', None)
        time_range = kwargs.get('time_range', None)
        art_type = kwargs.get('art_type', None)
        creator = kwargs.get('creator', None)
        material = kwargs.get('material', None)
        length = kwargs.get('length', None)
        height = kwargs.get('height', None)
        width = kwargs.get('width', None)
        diameter = kwargs.get('diameter', None)
        location = kwargs.get('location', None)
        description = kwargs.get('description', None)
        additional_information = kwargs.get('additional_information', None)
        interdisciplinary_context = kwargs.get('interdisciplinary_context', None)

        if get_jwt_claims() == admin_claim:

            if not MuseumObjectModel.objects(object_id=object_id):
                size = dict(length=length, height=height, width=width, diameter=diameter)
                museum_object = MuseumObjectModel(object_id=object_id, category=category, sub_category=sub_category,
                                                  title=title, time_range=time_range, year=year,
                                                  art_type=art_type, creator=creator, material=material,
                                                  size=size, location=location, description=description,
                                                  additional_information=additional_information,
                                                  interdisciplinary_context=interdisciplinary_context)
                if picture is not None:
                    pics = []
                    for pic in picture:
                        x = PictureModel()
                        x.picture.put(pic, content_type='image/png')
                        x.save()
                        pics.append(x)
                    museum_object.update(set__picture=pics)
                museum_object.save()
                return CreateMuseumObject(ok=BooleanField(boolean=True), museum_object=museum_object)

            else:
                return CreateMuseumObject(ok=BooleanField(boolean=False), museum_object=None)
        else:
            return CreateMuseumObject(ok=BooleanField(boolean=False), museum_object=None)


class UpdateMuseumObject(Mutation):
    """ Modify a Museum Object.
        Parameters: token, String, required, valid jwt access token with the admin claim
                    objectId, String, required, inventory id of the object in the museum
                    category, String, optional, category of the object in the museum. 'Abteilung'
                    subCategory, String, optional, sub-category of the object in the museum. 'Sammlungsbereich'
                    title, String, optional, name of the object
                    year, List of Strings, optional, year the object was created/found
                    picture, List of Upload, optional, pictures in png format
                    art_type, List of Strings, optional, classification of the object e.g. 'painting'
                    creator, List of Strings, optional, creators of the object
                    material, List of Strings, optional, materials the object is made of
                    width, Int, optional, width of the object in centimeters
                    height, Int, optional, height of the object in centimeters
                    length, Int, length of the object in centimeters
                    diameter, optional, Int, diameter of the object in centimeters
                    location, optional, List of Strings, optional, locations the object was made/found at
                    description, optional, String, optional, description of the object
                    interdisciplinary_context, String, optional, interdisciplinary relations of the object
        returns the updated object and True if successful
        returns Null and False if token did not belong to admin or object with that id does not exist
        returns Null and an empty value for ok if token was invalid """

    class Arguments:
        object_id = String(required=True)
        token = String(required=True)
        category = String()
        sub_category = String()
        time_range = String()
        title = String()
        year = List(String)
        picture = List(Upload)
        art_type = List(String)
        creator = List(String)
        material = List(String)
        width = Int()
        height = Int()
        length = Int()
        diameter = Int()
        location = List(String)
        additional_information = String()
        description = String()
        interdisciplinary_context = List(String)

    museum_object = Field(lambda: MuseumObject)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, object_id, **kwargs):
        if get_jwt_claims() == admin_claim:
            if not MuseumObjectModel.objects(object_id=object_id):
                return UpdateMuseumObject(ok=BooleanField(boolean=False), museum_object=None)
            else:
                museum_object = MuseumObjectModel.objects.get(object_id=object_id)
                category = kwargs.get('category', None)
                sub_category = kwargs.get('sub_category', None)
                title = kwargs.get('title', None)
                time_range = kwargs.get('time_range', None)
                year = kwargs.get('year', None)
                picture = kwargs.get('picture', None)
                art_type = kwargs.get('art_type', None)
                creator = kwargs.get('creator', None)
                material = kwargs.get('material', None)
                length = kwargs.get('length', None)
                height = kwargs.get('height', None)
                width = kwargs.get('width', None)
                diameter = kwargs.get('diameter', None)
                location = kwargs.get('location', None)
                description = kwargs.get('description', None)
                additional_information = kwargs.get('additional_information', None)
                interdisciplinary_context = kwargs.get('interdisciplinary_context', None)

                if category is not None:
                    museum_object.update(set__category=category)
                if sub_category is not None:
                    museum_object.update(set__sub_category=sub_category)
                if title is not None:
                    museum_object.update(set__title=title)
                if year is not None:
                    museum_object.update(set__year=year)
                if picture is not None:
                    pics = []
                    for pic in picture:
                        x = PictureModel()
                        x.picture.put(pic, content_type='image/png')
                        x.save()
                        pics.append(x)
                    museum_object.update(set__picture=pics)
                if art_type is not None:
                    museum_object.update(set__art_type=art_type)
                if time_range is not None:
                    museum_object.update(set__time_range=time_range)
                if additional_information is not None:
                    museum_object.update(set__additional_information=additional_information)
                if creator is not None:
                    museum_object.update(set__creator=creator)
                if material is not None:
                    museum_object.update(set__material=material)
                if museum_object.size is not None:
                    if width is not None:
                        museum_object.update(set__size__width=width)
                    if length is not None:
                        museum_object.update(set__size__length=length)
                    if height is not None:
                        museum_object.update(set__size__height=height)
                    if diameter is not None:
                        museum_object.update(set__size__diameter=diameter)
                if location is not None:
                    museum_object.update(set__location=location)
                if description is not None:
                    museum_object.update(set__description=description)
                if interdisciplinary_context is not None:
                    museum_object.update(set__interdisciplinary_context=interdisciplinary_context)
                museum_object.save()
                museum_object.reload()

                return UpdateMuseumObject(ok=BooleanField(boolean=True), museum_object=museum_object)
        else:
            return UpdateMuseumObject(ok=BooleanField(boolean=False), museum_object=None)


class CreateAdmin(Mutation):
    """Create a user account.
           Parameters: username, String, name of the account. has to be unique
                       password, String, password, no requirements, saved as a hash
           if successful returns the created user and ok=True
           fails if the username is already taken. returns Null and False in that case
    """

    class Arguments:
        username = String(required=True)
        password = String(required=True)

    user = Field(lambda: Admin)
    ok = Boolean()

    def mutate(self, info, username, password):
        if not AdminModel.objects(username=username):
            user = AdminModel(username=username, password=generate_password_hash(password))
            user.save()
            return CreateAdmin(user=user, ok=True)
        else:
            return CreateAdmin(user=None, ok=False)


class DeleteMuseumObject(Mutation):
    """Delete a Museum Object.
       Parameters: token, String, valid jwt access token with the admin claim
                   objectId, String, museum inventory id of the object to be deleted
        returns True if successful
        returns false if token does not have admin claim
        returns empty value if token was invalid
        is successful if object does not exist
        deletes all references to the object in favourites, tours, questions
         """

    class Arguments:
        token = String(required=True)
        object_id = String(required=True)

    ok = Field(ProtectedBool)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, object_id):
        if get_jwt_claims() == admin_claim:
            if MuseumObjectModel.objects(object_id=object_id):
                museum_object = MuseumObjectModel.objects.get(object_id=object_id)
                pictures = museum_object.picture
                for picture in pictures:
                    picture.delete()
                favourites = FavouritesModel.objects(contains__favouvite_objects=museum_object)
                for favourite in favourites:
                    objects = favourite.favourite_objects
                    objects.remove(museum_object)
                    favourite.update(set__favourite_objects=objects)
                    favourite.save()
                questions = QuestionModel.objects(contains__linked_objects=museum_object)
                for question in questions:
                    linked = question.linked_objects
                    linked.remove(museum_object)
                    question.update(set__linked_objects=linked)
                checkpoints = ObjectCheckpointModel.objects(museum_object=museum_object)
                for checkpoint in checkpoints:
                    checkpoint.delete()
                museum_object.delete()
            return DeleteMuseumObject(ok=BooleanField(boolean=True))

        else:
            return DeleteMuseumObject(ok=BooleanField(boolean=False))


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
        user = AdminModel.objects(username=username)[0]
        user.update(set__password=generate_password_hash(password))
        user.save()
        return ChangePassword(ok=BooleanField(boolean=True))


class Auth(Mutation):
    """Login. Create a session and jwt access and refresh tokens.
       Parameters: username, String, the username of the account you wish to log in to
                   password, String, the password of the account. password is hashed and compared to the saved hash.
        if successful returns a jwt accessToken (String), a jwt refresh token (String) and True
            inserts the admin claim to the token's user claims
        if unsuccessful because the user does not exist or the password was invalid returns Null Null and False"""

    class Arguments:
        username = String(required=True)
        password = String(required=True)

    access_token = String()
    refresh_token = String()
    ok = Boolean()

    @classmethod
    def mutate(cls, _, info, username, password):
        if not (AdminModel.objects(username=username) and check_password_hash(
                AdminModel.objects(username=username)[0].password, password)):
            return Auth(ok=False)
        else:
            return Auth(access_token=create_access_token(username, user_claims=admin_claim),
                        refresh_token=create_refresh_token(username, user_claims=admin_claim),
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
        claim = get_jwt_claims()
        if claim == admin_claim:
            return Refresh(new_token=create_access_token(identity=current_user, user_claims=admin_claim))
        else:
            return Refresh(new_token=None)


class CreateCode(Mutation):
    """Create an account promotion code.
       Parameter: token, String, valid jwt access token with the admin claim
       returns a code and True if successful
       returns Null and false if token does not have admin claim
       returns Null and empty value for ok if token is invalid
       the created code is a random 5-character string """

    class Arguments:
        token = String(required=True)

    ok = ProtectedBool()
    code = ProtectedString()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info):
        if get_jwt_claims() == admin_claim:
            letters = string.ascii_lowercase
            code_string = ''.join(random.choice(letters) for i in range(5))
            code = CodeModel(code=code_string)
            code.save()
            return CreateCode(ok=BooleanField(boolean=True), code=StringField(string=code_string))
        else:
            return CreateCode(ok=BooleanField(boolean=False), code=None)


class DemoteUser(Mutation):
    """Remove a user's producer status.
       Parameter: token, String, valid jwt access token with the admin claim
                  username, String, name of the user you want to demote
        returns the updated user object and True if successful
        returns Null and False if the user did not exist or the token does not have the admin claim
        returns Null and an empty value for ok if the token was invalid
    """

    class Arguments:
        username = String(required=True)
        token = String(required=True)

    ok = ProtectedBool()
    user = Field(User)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, username):
        if get_jwt_claims() == admin_claim:
            if UserModel.objects(username=username):
                user = UserModel.objects.get(username=username)
                user.update(set__producer=False)
                user.save()
                user = UserModel.objects.get(username=username)
                return DemoteUser(ok=BooleanField(boolean=True), user=user)
            else:
                return DemoteUser(ok=BooleanField(boolean=False), user=None)
        else:
            return DemoteUser(ok=BooleanField(boolean=False), user=None)


class DeleteUser(Mutation):
    """Delete a user account
       Parameters: token, String, valid jwt access token with the admin claim
                   username, String, name of the account you want to delete
        returns True if successful
        returns False if token does not have the admin claim
        returns empty value if token was invalid
        successful if the user does not exist
        deletes all answers, tours, questions and favourites of the user
    """

    class Arguments:
        username = String(required=True)
        token = String(required=True)

    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, username):
        if get_jwt_claims() == admin_claim:
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
            return DeleteUser(ok=BooleanField(boolean=True))

        else:
            return DeleteUser(ok=BooleanField(boolean=False))


class DenyReview(Mutation):
    """  Deny a tour that has been submitted for review.
         Parameters: token, String, valid jwt access token with the admin claim
                     tourId, String, document id of the tour
         returns the updated tour object and True if successful
         returns Null and False if tour does not exist or token does not have admin claim
         returns Null and empty value if token was invalid
         sets the tours status field back to private
    """

    class Arguments:
        token = String(required=True)
        tour_id = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id):
        if get_jwt_claims() == admin_claim:
            if TourModel.objects(id=tour_id):
                tour = TourModel.objects.get(id=tour_id)
                tour.update(set__status='private')
                tour.save()
                tour.reload()
                return DenyReview(ok=BooleanField(boolean=True), tour=tour)
            else:
                return DenyReview(ok=BooleanField(boolean=False), tour=None)
        else:
            return DenyReview(ok=BooleanField(boolean=False), tour=None)


class AcceptReview(Mutation):
    """  Accept a tour that has been submitted for review.
         Parameters: token, String, valid jwt access token with the admin claim
                     tourId, String, document id of the tour
         returns the updated tour object and True if successful
         returns Null and False if tour does not exist or token does not have admin claim
         returns Null and empty value if token was invalid
         sets the tours status field back to featured
    """

    class Arguments:
        token = String(required=True)
        tour = String(required=True)

    ok = Field(ProtectedBool)
    tour_id = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id):
        if get_jwt_claims() == admin_claim:
            if TourModel.objects(id=tour_id):
                tour = TourModel.objects.get(id=tour_id)
                tour.update(set__status='featured')
                tour.save()
                tour.reload()
                return DenyReview(ok=BooleanField(boolean=True), tour=tour)
            else:
                return DenyReview(ok=BooleanField(boolean=False), tour=None)
        else:
            return DenyReview(ok=BooleanField(boolean=False), tour=None)


class ReadFeedback(Mutation):
    """Read App Feedback.
       Parameter: token, String, valid jwt access token with the admin claim
                  feedback, String, object id of the feedback to be read
        returns True if successful
        returns False if token does not have admin claim or feedback object does not exist
        returns empty value if token was invalid
        sets the feedback's read field to True
        works on feedback that has already been read """

    class Arguments:
        token = String(required=True)
        feedback = String(required=True)

    ok = Field(ProtectedBool)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, feedback):
        if get_jwt_claims() == admin_claim:
            if not AppFeedbackModel.objects(id=feedback):
                return ReadFeedback(ok=BooleanField(boolean=False))
            else:
                feedback = AppFeedbackModel.objects.get(id=feedback)
                feedback.update(set__read=True)
                feedback.save()
                return ReadFeedback(ok=BooleanField(boolean=True))
        else:
            return ReadFeedback(ok=BooleanField(boolean=False))


class CreateBadge(Mutation):
    """
        Create a new Badge that Users can earn.
        Parameters:
                token, String, valid jwt access token of an admin
                name, String, name of the badge
                badge_id, String, unique ID of the badge
                picture, Upload, expects a png image. used as icon for the badge
                description, String, description text of the badge
                cost, Int, number of points needed to receive the badge
        if successful returns the new badge object and True
        if unsuccessful because token was invalid returns an empty value for ok
        if unsuccessful because token did not possess admin claim or because badge id was taken returns Null and False
    """
    class Arguments:
        token = String(required=True)
        name = String(required=True)
        badge_id = String(required=True)
        picture = Upload(required=True)
        description = String(required=True)
        cost = Int(required=True)

    ok = Field(ProtectedBool)
    badge = Field(Badge)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, name, badge_id, picture, description, cost):
        # ensure caller is admin
        if get_jwt_claims() == admin_claim:
            # ensure badge id is unique
            if not BadgeModel.objects(id=badge_id):
                badge = BadgeModel(id=badge_id, name=name, description=description, cost=cost)
                badge.picture.put(picture, content_type='image/png')
                badge.save()
                badge.reload()
                # add badge to the progress dict of all users.
                for user in UserModel.objects.all():
                    badges = user.badge_progress
                    badges[badge_id] = 0
                    user.update(set__badge_progress=badges)
                    user.save()
                return CreateBadge(badge=badge, ok=BooleanField(boolean=True))
            else:
                return CreateBadge(badge=None, ok=BooleanField(boolean=False))
        else:
            return CreateBadge(badge=None, ok=BooleanField(boolean=False))


class CreateProfilePicture(Mutation):
    """
        create a new profile picture for users to choose.
        Parameters:
            token, String, valid jwt access token of an admin
            picture, Upload, the profile picture in png format
        if successful returns True
        if unsuccessful because token was invalid returns empty value
        if unsuccessful because token did not belong to admin returns False
    """
    class Arguments:
        token = String(required=True)
        picture = Upload(required=True)

    ok = Field(ProtectedBool)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, picture):
        if not get_jwt_claims() == admin_claim:
            return CreateProfilePicture(ok=BooleanField(boolean=False))
        pic = ProfilePictureModel()
        pic.picture.put(picture, content_type='image/png')
        pic.save()
        return CreateProfilePicture(ok=BooleanField(boolean=True))


class CreatePicture(Mutation):
    class Arguments:
        token = String(required=True)
        picture = Upload(required=True)
        description = String()

    ok = Field(ProtectedBool)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, picture, description=None):
        if not get_jwt_claims() == admin_claim:
            return CreatePicture(ok=BooleanField(boolean=False))
        pic = PictureModel(description=description)
        pic.picture.put(picture, content_type='image/png')
        pic.save()
        return CreatePicture(ok=BooleanField(boolean=True))

# TODO:
#       update badge
#       update picture
#       update profile picture


class EditCheckpoint(Mutation):
    """
        Allows admins to edit arbitrary checkpoints e.g. to correct spelling mistakes in tours submitted for review

    """
    class Arguments:
        token = String(required=True)
        checkpoint_id = String(required=True)
        text = String()
        object_id = String()
        picture_id = String()
        question = String()
        linked_objects = List(String)
        possible_answers = List(String)
        correct_answers = List(Int)
        max_choices = Int()

    checkpoint = Field(lambda: CheckpointUnion)
    ok = Field(ProtectedBool)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, checkpoint_id, **kwargs):
        # assert caller is admin
        if not get_jwt_claims() == admin_claim:
            return EditCheckpoint(checkpoint=None, ok=BooleanField(boolean=False))
        # assert checkpoint exists
        if not CheckpointModel.objects(id=checkpoint_id):
            return EditCheckpoint(checkpoint=None, ok=BooleanField(boolean=False))
        # get checkpoint object
        checkpoint = CheckpointModel.objects.get(id=checkpoint_id)
        # get all the optional arguments
        text = kwargs.get('text', None)
        object_id = kwargs.get('object_id', None)
        picture_id = kwargs.get('picture_id', None)
        question = kwargs.get('question', None)
        linked_objects = kwargs.get('linked_objects', None)
        possible_answers = kwargs.get('possible_answers', None)
        correct_answers = kwargs.get('correct_answers', None)
        max_choices = kwargs.get('max_choices', None)
        # treat checkpoint update depending on the type of the checkpoint
        if isinstance(checkpoint, ObjectCheckpointModel):
            # assert new object exists
            if object_id is not None:
                if not MuseumObjectModel.objects(object_id=object_id):
                    return EditCheckpoint(checkpoint=None, ok=BooleanField(boolean=False))
                museum_object = MuseumObjectModel.objects.get(object_id=object_id)
                checkpoint.update(set__museum_object=museum_object)
                # text may be changed on any checkpoint
            if text is not None:
                checkpoint.update(set__text=text)
            checkpoint.save()
            checkpoint.reload()
            return EditCheckpoint(checkpoint=checkpoint, ok=BooleanField(boolean=True))
        elif isinstance(checkpoint, PictureCheckpointModel):
            # assert new picture exists
            if picture_id is not None:
                if not PictureModel.objects(id=picture_id):
                    return EditCheckpoint(checkpoint=None, ok=BooleanField(boolean=False))
                pic = PictureModel.objects.get(id=picture_id)
                checkpoint.update(set__picture=pic)
            if text is not None:
                checkpoint.update(set__text=text)
            checkpoint.save()
            checkpoint.reload()
            return EditCheckpoint(checkpoint=checkpoint, ok=BooleanField(boolean=True))
        # check MCQuestion first because a MCQuestion would pass the check for isinstance(checkpoint,QuestionModel)
        elif isinstance(checkpoint, MCQuestionModel):
            # question text is inherited from question
            if question is not None:
                checkpoint.update(set__question=question)
            if possible_answers is not None:
                checkpoint.update(set__possible_answers=possible_answers)
            if correct_answers is not None:
                checkpoint.update(set__correct_answers=correct_answers)
            if max_choices is not None:
                checkpoint.update(set__max_choices=max_choices)
            # linked objects are also inherited from question
            if linked_objects is not None:
                checkpoint.update(set__linked_objects=linked_objects)
            if text is not None:
                checkpoint.update(set__text=text)
            checkpoint.save()
            checkpoint.reload()
            return EditCheckpoint(checkpoint=checkpoint, ok=BooleanField(boolean=True))
        elif isinstance(checkpoint, QuestionModel):
            if question is not None:
                checkpoint.update(set__question=question)
            if linked_objects is not None:
                checkpoint.update(set__linked_objects=linked_objects)
            if text is not None:
                checkpoint.update(set__text=text)
            checkpoint.save()
            checkpoint.reload()
            return EditCheckpoint(checkpoint=checkpoint, ok=BooleanField(boolean=True))
        # last remaining option is a basic text checkpoint
        else:
            if text is not None:
                checkpoint.update(set__text=text)
            checkpoint.save()
            checkpoint.reload()
            return EditCheckpoint(checkpoint=checkpoint, ok=BooleanField(boolean=True))


class Mutation(ObjectType):
    create_user = CreateAdmin.Field()
    auth = Auth.Field()
    refresh = Refresh.Field()
    change_password = ChangePassword.Field()
    create_museum_object = CreateMuseumObject.Field()
    update_museum_object = UpdateMuseumObject.Field()
    delete_museum_object = DeleteMuseumObject.Field()
    create_code = CreateCode.Field()
    demote_user = DemoteUser.Field()
    delete_user = DeleteUser.Field()
    deny_review = DenyReview.Field()
    accept_review = AcceptReview.Field()
    read_feedback = ReadFeedback.Field()
    create_badge = CreateBadge.Field()
    create_picture = CreatePicture.Field()
    create_profile_picture = CreateProfilePicture.Field()
    edit_checkpoint = EditCheckpoint.Field()
