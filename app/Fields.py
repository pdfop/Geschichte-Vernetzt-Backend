from graphene_mongo import MongoengineObjectType
from graphene import Union
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
from models.Picture import Picture as PictureModel
from models.Badge import Badge as BadgeModel
from models.Checkpoint import Checkpoint as CheckpointModel
from models.MultipleChoiceAnswer import MultipleChoiceAnswer as MCAnswerModel
from models.MultipleChoiceQuestion import MultipleChoiceQuestion as MCQuestionModel
from models.PictureCheckpoint import PictureCheckpoint as PictureCheckpointModel
from models.ObjectCheckpoint import ObjectCheckpoint as ObjectCheckpointModel
from models.ProfilePicture import ProfilePicture as ProfilePictureModel
"""
    This file contains the models used in GraphQL. 
    A model for a type is only needed when it is returned by a GraphQL function.  
"""


class Tour(MongoengineObjectType):
    class Meta:
        model = TourModel


class Question(MongoengineObjectType):
    class Meta:
        model = QuestionModel


class MCQuestion(MongoengineObjectType):
    class Meta:
        model = MCQuestionModel


class Answer(MongoengineObjectType):
    class Meta:
        model = AnswerModel


class MCAnswer(MongoengineObjectType):
    class Meta:
        model = MCAnswerModel


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


class Picture(MongoengineObjectType):
    class Meta:
        model = PictureModel


class ProfilePicture(MongoengineObjectType):
    class Meta:
        model = ProfilePictureModel


class Badge(MongoengineObjectType):
    class Meta:
        model = BadgeModel


class Checkpoint(MongoengineObjectType):
    class Meta:
        model = CheckpointModel


class PictureCheckpoint(MongoengineObjectType):
    class Meta:
        model = PictureCheckpointModel


class ObjectCheckpoint(MongoengineObjectType):
    class Meta:
        model = ObjectCheckpointModel


class CheckpointUnion(Union):
    class Meta:
        types = (PictureCheckpoint, ObjectCheckpoint, MCQuestion, Question, Checkpoint)

    @classmethod
    def resolve_type(cls, instance, info):
        if isinstance(instance, ObjectCheckpoint):
            return ObjectCheckpoint
        elif isinstance(instance, PictureCheckpoint):
            return PictureCheckpoint
        elif isinstance(instance, MCQuestion):
            return MCQuestion
        elif isinstance(instance, Question):
            return Question
        elif isinstance(instance, Checkpoint):
            return Checkpoint

