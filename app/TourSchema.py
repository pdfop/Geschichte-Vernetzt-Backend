from flask_graphql_auth import mutation_jwt_required, get_jwt_identity, query_jwt_required
from graphene import Mutation, String, List, Int, Field, Schema, ObjectType
from app.ProtectedFields import ProtectedBool
from app.ProtectedFields import BooleanField
from models.User import User as UserModel
from models.Tour import Tour as TourModel
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.Question import Question as QuestionModel
from models.Answer import Answer as AnswerModel
from models.TourFeedback import TourFeedback as TourFeedbackModel
from app.Fields import Tour, Question, Answer, TourFeedback, MuseumObject


class CreateTour(Mutation):
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
    class Arguments:
        tour = String(required=True)
        token = String(required=True)
        session_id = Int(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour, session_id):
        if TourModel.objects(id=tour):
            tour = TourModel.objects.get(id=tour)
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
        tour = String(required=True)
        token = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour):
        if TourModel.objects(id=tour):
            tour = TourModel.objects.get(id=tour)
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
    class Arguments:
        token = String(required=True)
        tour = String(required=True)
        question_id = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour, question_id):
        if TourModel.objects(id=tour):
            tour = TourModel.objects.get(id=tour)
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
        token = String(required=True)
        tour = String(required=True)
        username = String(required=True)

    ok = Field(ProtectedBool)
    tour = Field(Tour)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, tour, username):
        if TourModel.objects(id=tour):
            tour = TourModel.objects.get(id=tour)
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
    class Arguments:
        tour = String(required=True)
        token = String(required=True)
        rating = Int(required=True)
        review = String(required=True)

    ok = Field(ProtectedBool)
    feedback = Field(TourFeedback)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, rating, tour, review):
        if TourModel.objects(id=tour):
            tour = TourModel.objects.get(id=tour)
            feedback = TourFeedbackModel(rating=rating, review=review, tour=tour)
            feedback.save()
            return SubmitFeedback(ok=BooleanField(boolean=True), feedback=feedback)
        else:
            return SubmitFeedback(ok=BooleanField(boolean=False), feedback=None)


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
    submit_feedback = SubmitFeedback.Field()


class Query(ObjectType):
    # queries related to tours
    tour = List(Tour, token=String(), tour=String())
    my_tours = List(Tour, token=String())
    owned_tours = List(Tour, token=String())
    feedback = List(TourFeedback, token=String(), tour=String())

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
        tour = TourModel.objects.get(id=tour)
        if user in tour.users:
            return [tour]
        else:
            return []

    @classmethod
    @query_jwt_required
    def resolve_owned_tours(cls, _, info):
        username = get_jwt_identity()
        user = UserModel.objects.get(username=username)
        return list(TourModel.objects(owner=user))

    @classmethod
    @query_jwt_required
    def resolve_feedback(cls, _, info, tour):
        user = UserModel.objects.get(username=get_jwt_identity())
        if TourModel.objects(id=tour):
            tour = TourModel.objects.get(id=tour)
        if tour.owner == user:
            return list(TourFeedbackModel.objects(tour=tour))
        else:
            return []

    # queries related to questions and answers
    answers_to_question = List(Question, token=String(), question=String())
    answers_by_user = List(Answer, tour=String(), token=String(), user=String())
    my_answers = List(Answer, token=String(), tour=String())

    @classmethod
    @query_jwt_required
    def resolve_answers_to_question(cls, _, info, question):
        if QuestionModel.objects(id=question):
            question = QuestionModel.objects.get(id=question)
            return list(AnswerModel.objects(question=question))
        else:
            return None

    # TODO: when adding public and private answers gate private answers to the tour owner

    @classmethod
    @query_jwt_required
    def resolve_answers_by_user(cls, _, info, username, tour):
        if UserModel.objects(username=username):
            user = UserModel.objects.get(username=username)
            if TourModel.objects(id=tour):
                tour = TourModel.objects.get(id=tour)
                answers = []
                for answer in tour.answers:
                    if answer.user == user:
                        answers.append(answer)
                return answers
        return None

    @classmethod
    @query_jwt_required
    def resolve_my_answers(cls, _, info, tour):
        if TourModel.objects(id=tour):
            tour = TourModel.objects.get(id=tour)
            user = UserModel.objects.get(username=get_jwt_identity())
            answers = []
            for answer in tour.answers:
                if answer.user == user:
                    answers.append(answer)
            return answers
        return None

    # master query for objects
    museum_object = List(MuseumObject, object_id=String())

    def revolve_museum_object(cls, _, info, **kwargs):
        object_id = kwargs.get('object_id', 1)
        museum_object = MuseumObjectModel.objects(object_id=object_id)
        return list(museum_object)


tour_schema = Schema(query=Query, mutation=Mutation)
