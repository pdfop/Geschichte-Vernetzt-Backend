from flask_graphql_auth import mutation_jwt_required, get_jwt_identity, query_jwt_required
from graphene import Mutation, String, List, Int, Field, Schema, ObjectType
from graphene_mongo import MongoengineObjectType
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.Question import Question as QuestionModel
from models.Answer import Answer as AnswerModel
from models.Tour import Tour as TourModel
from models.User import User as UserModel
from app.ProtectedFields import ProtectedBool
from app.ProtectedFields import BooleanField


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
        session_id = Int(required=True)

    tour = Field(lambda: Tour)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour_id, name, session_id):
        if not TourModel.objects(tour_id=tour_id):
            owner_name = get_jwt_identity()
            if UserModel.objects(username=owner_name):
                owner = UserModel.objects.get(username=owner_name)
                if owner.teacher:
                    users = [owner]
                    tour = TourModel(tour_id=tour_id, owner=owner, name=name, users=users, session_id=session_id)
                    tour.save()
                    return CreateTour(tour=tour, ok=BooleanField(boolean=True))
                else:
                    return CreateTour(tour=None, ok=BooleanField(boolean=False))
        else:
            return CreateTour(tour=None, ok=BooleanField(boolean=False))


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
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            if QuestionModel.objects(question_id=question):
                question = QuestionModel.objects.get(question_id=question)
            else:
                return CreateAnswer(answer=None, ok=BooleanField(boolean=False))
            if not AnswerModel.objects(question=question, user=user):
                answer = AnswerModel(question=question, user=user, answer=answer, answer_id=answer_id)
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
        linked_objects = List(of_type=Int)
        question_id = Int(required=True)
        question_text = String(required=True)

    question = Field(Question)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, question_id, question_text, linked_objects):
        username = get_jwt_identity()
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            if user.teacher:
                if not QuestionModel.objects(question_id=question_id):
                    question = QuestionModel(question_id=question_id, linked_objects=linked_objects,
                                             question=question_text)
                    question.save()
                    return CreateQuestion(question=question,
                                          ok=BooleanField(boolean=True))
                else:
                    question = QuestionModel.objects.get(question_id=question_id)
                    question.update(set__question=question_text)
                    question.save()
                    question.reload()
                    question.update(set__linked_objects=linked_objects)
                    question.save()
                    question.reload()
                    return CreateQuestion(question=question, ok=BooleanField(boolean=True))
            else:
                return CreateQuestion(question=None, ok=BooleanField(boolean=False))


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
        if TourModel.objects(tour_id=tour_id):
            tour = TourModel.objects.get(tour_id=tour_id)
            if tour.owner.username == get_jwt_identity():
                if MuseumObjectModel.objects(object_id=object_id):
                    museum_object = MuseumObjectModel.objects.get(object_id=object_id)
                    referenced = tour.referenced_objects
                    referenced.append(museum_object)
                    tour.update(set__referenced_objects=referenced)
                    tour.save()
                    tour = TourModel.objects.get(tour_id=tour_id)
                    return AddObject(ok=BooleanField(boolean=True), tour=tour)
                else:
                    return AddObject(ok=BooleanField(boolean=False), tour=None)
            else:
                return AddObject(ok=BooleanField(boolean=False), tour=None)
        else:
            return AddObject(ok=BooleanField(boolean=False), tour=None)


# TODO: bug where you cannot query the list of question of a tour in the return of this


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
        if TourModel.objects(tour_id=tour_id):
            tour = TourModel.objects.get(tour_id=tour_id)
            if tour.owner.username == get_jwt_identity():
                if QuestionModel.objects(question_id=question):
                    question = QuestionModel.objects.get(question_id=question)
                    questions = tour.questions
                    questions.append(question)
                    tour.update(set__questions=questions)
                    tour.save()
                    tour = TourModel.objects.get(tour_id=tour_id)
                    return AddQuestion(ok=BooleanField(boolean=True), tour=tour)
                else:
                    return AddQuestion(ok=BooleanField(boolean=False), tour=None)
            else:
                return AddQuestion(ok=BooleanField(boolean=False), tour=None)
        else:
            return AddQuestion(ok=BooleanField(boolean=False), tour=None)


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
        if TourModel.objects(tour_id=tour_id):
            tour = TourModel.objects.get(tour_id=tour_id)
            username = get_jwt_identity()
            if UserModel.objects(username=username):
                user = UserModel.objects.get(username=username)
                if user in tour.users:
                    answers = tour.answers
                    answers[question_id].update({user.username: answer_id})
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
    class Arguments:
        tour = Int(required=True)
        token = String(required=True)
        session_id = Int(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour, session_id):
        if TourModel.objects(tour_id=tour):
            tour = TourModel.objects.get(tour_id=tour)
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
    class Arguments:
        tour = Int(required=True)
        token = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour):
        if TourModel.objects(tour_id=tour):
            tour = TourModel.objects.get(tour_id=tour)
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
    class Arguments:
        token = String(required=True)
        tour = Int(required=True)
        session_id = Int(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour, session_id):
        if TourModel.objects(tour_id=tour):
            tour = TourModel.objects.get(tour_id=tour)
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
    class Arguments:
        token = String(required=True)
        tour = Int(required=True)
        object_id = Int(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour, object_id):
        if TourModel.objects(tour_id=tour):
            tour = TourModel.objects.get(tour_id=tour)
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

# TODO: chain delete answers to the question


class RemoveQuestion(Mutation):
    class Arguments:
        token = String(required=True)
        tour = Int(required=True)
        question_id = Int(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour, question_id):
        if TourModel.objects(tour_id=tour):
            tour = TourModel.objects.get(tour_id=tour)
            username = get_jwt_identity()
            if tour.owner.username == username:
                if QuestionModel.objects(question_id=question_id):
                    question = QuestionModel.objects.get(question_id=question_id)
                    questions = tour.questions
                    if question in questions:
                        questions.remove(question)
                    tour.update(set__questions=question)
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
        token = String(required=True)
        tour = Int(required=True)
        username = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour, username):
        if TourModel.objects(tour_id=tour):
            tour = TourModel.objects.get(tour_id=tour)
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


class Mutation(ObjectType):
    create_tour = CreateTour.Field()
    create_question = CreateQuestion.Field()
    create_answer = CreateAnswer.Field()
    add_question = AddQuestion.Field()
    add_answer = AddAnswer.Field()
    add_object = AddObject.Field()
    add_member = AddMember.Field()
    submit_review = SubmitReview.Field()
    update_session_id = UpdateSessionId.Field()
    remove_museum_object = RemoveMuseumObject.Field()
    remove_question = RemoveQuestion.Field()
    remove_user = RemoveUser.Field()


class Query(ObjectType):
    tour = List(Tour, token=String(), tour=Int())
    my_tours = List(Tour, token=String())
    museum_object = List(MuseumObject, object_id=Int())
    owned_tours = List(Tour, token=String())

    def revolve_museum_object(cls, _, info, **kwargs):
        object_id = kwargs.get('object_id', 1)
        museum_object = MuseumObjectModel.objects(object_id=object_id)
        return list(museum_object)

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
        tour = TourModel.objects.get(tour_id=tour)
        if user in tour.users:
            return [tour]
        else:
            return None

    @classmethod
    @query_jwt_required
    def resolve_owned_tours(cls, _, info):
        username = get_jwt_identity()
        user = UserModel.objects.get(username=username)
        return list(TourModel.objects(owner=user))


tour_schema = Schema(query=Query, mutation=Mutation)
