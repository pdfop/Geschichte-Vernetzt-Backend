from flask_graphql_auth import mutation_jwt_required, get_jwt_identity
from graphene import Mutation, String, List, Int, Field, Schema, ObjectType
from graphene_mongo import MongoengineObjectType
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.Question import Question as QuestionModel
from models.Answer import Answer as AnswerModel
from models.Tour import Tour as TourModel
from models.User import User as UserModel
from app.ProtectedFields import ProtectedBool
from app.ProtectedFields import BooleanField

# TODO: teacher permission check


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
        tour_id = Int(required=True)
        token = String(required=True)
        name = String(required=True)

    tour = Field(lambda: Tour)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id, name):
        if not TourModel.objects(tour_id=tour_id):
            owner_name = get_jwt_identity()
            owner = UserModel.objects.get(username=owner_name)
            tour = TourModel(tour_id=tour_id, owner=owner, name=name)
            tour.save()
            return CreateTour(tour=tour, ok=BooleanField(boolean=True))
        else:
            return CreateTour(tour=None, ok=BooleanField(boolean=False))

# TODO: overwrite / duplicate check


class CreateAnswer(Mutation):
    class Arguments:
        answer_id = Int(required=True)
        token = String(required=True)
        answer = String(required=True)
        question = Int(required=True)

    answer = Field(Answer)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, answer_id, answer, question):
        username = get_jwt_identity()
        user = UserModel.objects.get(username=username)
        question = QuestionModel.objects.get(question_id=question)
        answer = AnswerModel(question=question, username=user, answer=answer, answer_id=answer_id)
        answer.save()
        return CreateAnswer(answer=answer, ok=BooleanField(boolean=True))

# TODO: overwrite / duplicate check


class CreateQuestion(Mutation):
    class Arguments:
        token = String(required=True)
        linked_objects = List(of_type=Int)
        question_id = Int(required=True)
        question_text = String(required=True)

    question = Field(Question)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, question_id, question_text, linked_objects):
        question = QuestionModel(question_id=question_id, linked_objects=linked_objects, question=question_text)
        question.save()
        return CreateQuestion(question=question,
                              ok=BooleanField(boolean=True))


class AddObject(Mutation):
    class Arguments:
        tour_id = Int(required=True)
        object_id = Int(required=True)
        token = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id, object_id):
        tour = TourModel.objects.get(tour_id=tour_id)
        museum_object = MuseumObjectModel.objects.get(object_id=object_id)
        referenced = tour.referenced_objects
        referenced.append(museum_object)
        tour.update(set__referenced_objects=referenced)
        tour.save()
        tour = TourModel.objects.get(tour_id=tour_id)
        return AddObject(ok=BooleanField(boolean=True), tour=tour)

# TODO: bug where you cannot query the list of question of a turn in th return of this


# TODO: overwrite / duplicate check
# TODO: this might actually be redundant if questions are just identified by the keys in the answers dict

class AddQuestion(Mutation):
    class Arguments:
        tour_id = Int(required=True)
        question = Int(required=True)
        token = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id, question):
        tour = TourModel.objects.get(tour_id=tour_id)
        question = QuestionModel.objects.get(question_id=question)
        tour.update(set__questions=tour.questions.append(question))
        tour.save()
        tour = TourModel.objects.get(tour_id=tour_id)
        return AddQuestion(ok=BooleanField(boolean=True), tour=tour)


class AddAnswer(Mutation):
    class Arguments:
        answer_id = Int(required=True)
        tour_id = Int(required=True)
        question_id = Int(required=True)
        token = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id, question_id, answer_id):
        tour = TourModel.objects.get(tour_id=tour_id)
        username = get_jwt_identity()
        user = UserModel.objects.get(username=username)
        answers = tour.answers
        answers[str(question_id)] = {user.username: answer_id}
        tour.update(set__answers=answers)
        tour.save()
        tour = TourModel.objects.get(tour_id=tour_id)
        return AddAnswer(tour=tour, ok=BooleanField(boolean=True))


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


class Mutation(ObjectType):
    create_tour = CreateTour.Field()
    create_question = CreateQuestion.Field()
    create_answer = CreateAnswer.Field()
    add_question = AddQuestion.Field()
    add_answer = AddAnswer.Field()
    add_object = AddObject.Field()

class Query(ObjectType):
    tours = List(Tour)

    def resolve_tours(self, info):
        return list(TourModel.objects.all())


tour_schema = Schema(query=Query, mutation=Mutation)
