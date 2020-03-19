from mongoengine import *
from models.Question import Question


class MultipleChoiceQuestion(Question):
    """
        Model for Multiple Choice Questions.
    """
    possible_answers = ListField(StringField(), required=True)
    # answers are marked correct by adding the index in the possible_answers list here
    # e.g. if possible_answers contains 4 choices and the third is correct correct_answers = [2]
    # correct_answers is used to evaluate answers given by users. 
    correct_answers = ListField(IntField(), required=True)
    max_choices = IntField()
