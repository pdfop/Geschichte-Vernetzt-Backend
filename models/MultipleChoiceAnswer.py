from mongoengine import *
from models.MultipleChoiceQuestion import MultipleChoiceQuestion
from models.Answer import Answer


class MultipleChoiceAnswer(Answer):
    """
        Answer to a MultipleChoiceQuestion.
        Inherits from Answer.
        Saved in tour.answer
        Linked to a MultipleChoiceQuestion
    """
    # overwrites these from the parent class Answer to adapt to MultipleChoiceQuestion
    question = ReferenceField(document_type=MultipleChoiceQuestion, required=True, reverse_delete_rule=CASCADE)
    answer = ListField(IntField())
