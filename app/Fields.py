from graphene_mongo import MongoengineObjectType
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.Question import Question as QuestionModel
from models.Answer import Answer as AnswerModel
from models.Tour import Tour as TourModel
from models.User import User as UserModel
from models.Admin import Admin as AdminModel
from models.Code import Code as CodeModel
from models.AppFeedback import AppFeedback as AppFeedbackModel
from models.TourFeedback import TourFeedback as TourFeedbackModel
from models.Favourites import Favourites as FavouritesModel


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


class User(MongoengineObjectType):
    class Meta:
        model = UserModel


class Admin(MongoengineObjectType):
    class Meta:
        model = AdminModel


class Code(MongoengineObjectType):
    class Meta:
        model = CodeModel


class AppFeedback(MongoengineObjectType):
    class Meta:
        model = AppFeedbackModel


class TourFeedback(MongoengineObjectType):
    class Meta:
        model = TourFeedbackModel


class Favourites(MongoengineObjectType):
    class Meta:
        model = FavouritesModel
