from graphene import Mutation, String, List, Int, Field, Boolean
from graphene_mongo import MongoengineObjectType
from models.MuseumObject import MuseumObject as ObjectModel
from models.Question import Question as QuestionModel
from models.Answer import Answer as AnswerModel
from models.Tour import Tour as TourModel
from .UserSchema import User


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
        model = ObjectModel


class CreateTour(Mutation):
    class Arguments:
        sid = Int(required=True)
        owner = User(required=True)
        name = String(required=True)

    tour = Field(lambda: Tour)
    ok = Boolean()
    sid = Int()

    def mutate(self, info, sid, owner, name):
        if not TourModel.objects.get(id=sid) and not TourModel.objects.get(name=name):
            return CreateTour(tour=TourModel(id=sid, owner=owner, name=name), ok=True, sid=sid)
        else:
            return CreateTour(tour=None, ok=False, sid=0)


class CreateAnswer(Mutation):
    pass


class CreateQuestion(Mutation):
    pass


class AddObject(Mutation):
    pass


class AddQuestion(Mutation):
    pass


class AddAnswer(Mutation):
    pass


class AddMember(Mutation):
    pass

