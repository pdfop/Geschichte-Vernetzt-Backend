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
import string
import random
from app.ProtectedFields import StringField, ProtectedString, BooleanField, ProtectedBool
from app.Fields import Tour, MuseumObject, Admin, User, Code, AppFeedback

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

admin_claim = {'admin': True}


class CreateMuseumObject(Mutation):
    class Arguments:
        object_id = String(required=True)
        category = String(required=True)
        sub_category = String(required=True)
        title = String(required=True)
        token = String(required=True)
        year = List(String)
        picture = List(String)
        art_type = List(String)
        creator = List(String)
        material = List(String)
        size = String()
        location = List(String)
        description = String()
        interdisciplinary_context = String()

    museum_object = Field(lambda: MuseumObject)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, object_id, category, sub_category, title, **kwargs):
        year = kwargs.get('year', None)
        picture = kwargs.get('picture', None)
        art_type = kwargs.get('art_type', None)
        creator = kwargs.get('creator', None)
        material = kwargs.get('material', None)
        size = kwargs.get('size', None)
        location = kwargs.get('location', None)
        description = kwargs.get('description', None)
        interdisciplinary_context = kwargs.get('interdisciplinary_context', None)

        if get_jwt_claims() == admin_claim:

            if not MuseumObjectModel.objects(object_id=object_id):
                museum_object = MuseumObjectModel(object_id=object_id, category=category, sub_category=sub_category,
                                                  title=title, year=year, picture=picture, art_type=art_type,
                                                  creator=creator, material=material, size=size, location=location,
                                                  description=description,
                                                  interdisciplinary_context=interdisciplinary_context)
                museum_object.save()
                return CreateMuseumObject(ok=BooleanField(boolean=True), museum_object=museum_object)

            else:
                return CreateMuseumObject(ok=BooleanField(boolean=False), museum_object=None)
        else:
            return CreateMuseumObject(ok=BooleanField(boolean=False), museum_object=None)


class UpdateMuseumObject(Mutation):
    class Arguments:
        object_id = String(required=True)
        token = String(required=True)
        category = String()
        sub_category = String()
        title = String()
        year = String()
        picture = List(String)
        art_type = List(String)
        creator = List(String)
        material = List(String)
        size = String()
        location = List(String)
        description = String()
        interdisciplinary_context = String()

    museum_object = Field(lambda: MuseumObject)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, object_id, **kwargs):
        if get_jwt_claims() == admin_claim:
            if not MuseumObjectModel.objects(object_id=object_id):
                return UpdateMuseumObject(ok=BooleanField(boolean=False), museum_object=None)
            else:
                museum_object = MuseumObjectModel.objects(object_id=object_id)[0]

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

                if category is not None:
                    museum_object.update(set__category=category)
                    museum_object.save()
                    museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
                if sub_category is not None:
                    museum_object.update(set__sub_category=sub_category)
                    museum_object.save()
                    museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
                if title is not None:
                    museum_object.update(set__title=title)
                    museum_object.save()
                    museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
                if year is not None:
                    museum_object.update(set__year=year)
                    museum_object.save()
                    museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
                if picture is not None:
                    museum_object.update(set__picture=picture)
                    museum_object.save()
                    museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
                if art_type is not None:
                    museum_object.update(set__art_type=art_type)
                    museum_object.save()
                    museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
                if creator is not None:
                    museum_object.update(set__creator=creator)
                    museum_object.save()
                    museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
                if material is not None:
                    museum_object.update(set__material=material)
                    museum_object.save()
                    museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
                if size is not None:
                    museum_object.update(set__size=size)
                    museum_object.save()
                    museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
                if location is not None:
                    museum_object.update(set__location=location)
                    museum_object.save()
                    museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
                if description is not None:
                    museum_object.update(set__description=description)
                    museum_object.save()
                    museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
                if interdisciplinary_context is not None:
                    museum_object.update(set__interdisciplinary_context=interdisciplinary_context)
                    museum_object.save()
                    museum_object = MuseumObjectModel.objects(object_id=object_id)[0]

                return UpdateMuseumObject(ok=BooleanField(boolean=True), museum_object=museum_object)
        else:
            return UpdateMuseumObject(ok=BooleanField(boolean=False), museum_object=None)


class CreateAdmin(Mutation):
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
                questions = QuestionModel.objects(contains__linked_objects=museum_object)
                for question in questions:
                    linked = question.linked_objects
                    linked.remove(museum_object)
                    if not linked:
                        tours = TourModel.objects(contains__questions=question)
                        answers = AnswerModel.objects(question=question)
                        for tour in tours:
                            for answer in answers:
                                if answer in tour.answers:
                                    tour_answers = tour.answers
                                    tour_answers.remove(answer)
                                    tour.update(set__answers=tour_answers)
                                    tour.save()
                                    answer.delete()
                            tour_questions = tour.questions
                            tour_questions.remove(question)
                            tour.update(set__questions=tour_questions)
                            tour.save()
                            question.delete()
                    else:
                        question.update(set__linked_objects=linked)
                tours = TourModel.objects(contains__referenced_objects=museum_object)
                for tour in tours:
                    referenced = tour.referenced_objects
                    referenced.remove(museum_object)
                    tour.update(set__referenced_objects=referenced)
                    tour.save()
                museum_object.delete()

                return DeleteMuseumObject(ok=BooleanField(boolean=True))
            else:
                return DeleteMuseumObject(ok=BooleanField(boolean=False))
        else:
            return DeleteMuseumObject(ok=BooleanField(boolean=False))


class ChangePassword(Mutation):
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
        else:
            return DeleteUser(ok=BooleanField(boolean=False))


class DenyReview(Mutation):
    class Arguments:
        token = String(required=True)
        tour = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour):
        if get_jwt_claims() == admin_claim:
            if TourModel.objects(id=tour):
                tour = TourModel.objects.get(id=tour)
                tour.update(set__status='private')
                tour.save()
                tour.reload()
                return DenyReview(ok=BooleanField(boolean=True), tour=tour)
            else:
                return DenyReview(ok=BooleanField(boolean=False), tour=None)
        else:
            return DenyReview(ok=BooleanField(boolean=False), tour=None)


class AcceptReview(Mutation):
    class Arguments:
        token = String(required=True)
        tour = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour):
        if get_jwt_claims() == admin_claim:
            if TourModel.objects(id=tour):
                tour = TourModel.objects.get(id=tour)
                tour.update(set__status='featured')
                tour.save()
                tour.reload()
                return DenyReview(ok=BooleanField(boolean=True), tour=tour)
            else:
                return DenyReview(ok=BooleanField(boolean=False), tour=None)
        else:
            return DenyReview(ok=BooleanField(boolean=False), tour=None)


class ReadFeedback(Mutation):
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
