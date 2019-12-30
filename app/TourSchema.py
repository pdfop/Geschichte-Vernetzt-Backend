from flask_graphql_auth import mutation_jwt_required, get_jwt_identity
from graphene import Mutation, String, List, Int, Field, Boolean
from graphene_mongo import MongoengineObjectType
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.Question import Question as QuestionModel
from models.Answer import Answer as AnswerModel
from models.Tour import Tour as TourModel
from models.User import User as UserModel
from app.UserSchema import ProtectedBool
from app.UserSchema import BooleanField


class Tour(MongoengineObjectType):
    class Meta:
        model = TourModel


class Question(MongoengineObjectType):
    class Meta:
        model = QuestionModel


class Answer(MongoengineObjectType):
    class Meta:
        model = AnswerModel


class MuseumObject(MongoengineObjectType):
    class Meta:
        model = MuseumObjectModel


class CreateTour(Mutation):
    class Arguments:
        sid = Int(required=True)
        token = String(required=True)
        name = String(required=True)

    tour = Field(lambda: Tour)
    ok = Boolean()
    sid = Int()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, sid, name):

        if not TourModel.objects(id=sid) and not TourModel.objects(name=name):
            owner_name = get_jwt_identity()
            owner = UserModel.objects.get(username=owner_name)
            return CreateTour(tour=TourModel(id=sid, owner=owner, name=name), ok=True, sid=sid)
        else:
            return CreateTour(tour=None, ok=False, sid=0)


class CreateAnswer(Mutation):
    class Arguments:
        token = String(required=True)
        answer = String(required=True)
        question = Int(required=True)

    answer = Field(Answer)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, answer, question):
        username = get_jwt_identity()
        user = UserModel.objects.get(username=username)
        question = QuestionModel.objects.get(qid=question)
        return CreateAnswer(answer=AnswerModel(question=question, user=user, answer=answer),
                            ok=BooleanField(boolean=True))


class CreateQuestion(Mutation):
    class Arguments:
        token = String(required=True)
        linked_objects = List(default=[])
        qid = Int(required=True)
        question = String(required=True)

    question = Field(Question)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, qid, question, linked_objects):
        return CreateQuestion(question=QuestionModel(qid=qid, linked_objects=linked_objects, question=question),
                              ok=BooleanField(boolean=True))


class AddObject(Mutation):
    class Arguments:
        tour = Int(required=True)
        museum_object = Int(required=True)
        token = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour, museum_object):
        tour = TourModel.objects.get(id=tour)
        museum_object = MuseumObjectModel.objects.get(object_id=museum_object)
        tour.update(set__referenced_objects=tour.referenced_objects.append(museum_object))
        tour.save()
        tour = TourModel.objects.get(id=tour)
        return AddObject(ok=BooleanField(boolean=True), tour=tour)


class AddQuestion(Mutation):
    class Arguments:
        tour = Int(required=True)
        question = Int(required=True)
        token = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour, question):
        tour = TourModel.objects.get(id=tour)
        question = Question.objects.get(qid=question)
        tour.update(set__questions=tour.questions.append(question))
        tour.save()
        tour = TourModel.objects.get(id=tour)
        return AddQuestion(ok=BooleanField(boolean=True), tour=tour)


class AddAnswer(Mutation):
    class Arguments:
        tour = Int(required=True)
        question = Int(required=True)
        token = String(required=True)
        answer = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour, question, answer):
        tour = TourModel.objects.get(id=tour)
        question = Question.objects.get(qid=question)
        username = get_jwt_identity()
        user = UserModel.objects.get(username=username)
        answers = tour.answers
        answers[question].update({user: answer})
        tour.update(set__answers=answers)
        tour.save()
        tour = TourModel.objects.get(id=tour)
        return AddObject(ok=BooleanField(boolean=True), tour=tour)


class AddMember(Mutation):
    class Arguments:
        tour = Int(required=True)
        token = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour):
        tour = TourModel.objects.get(id=tour)
        username = get_jwt_identity()
        user = UserModel.objects.get(username=username)
        tour.update(set__users=tour.users.append(user))
        tour.save()
        tour = TourModel.objects.get(id=tour)
        return AddMember(ok=BooleanField(boolean=True), tour=tour)
