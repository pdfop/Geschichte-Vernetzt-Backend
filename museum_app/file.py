import io
from flask import Blueprint, send_file, request, jsonify

from app.WebMutations import admin_claim
from models.Answer import Answer
from models.Checkpoint import Checkpoint
from models.MultipleChoiceQuestion import MultipleChoiceQuestion
from models.Picture import Picture
from models.ProfilePicture import ProfilePicture
from models.Badge import Badge
from models.User import User
from flask_jwt_extended import jwt_required, get_jwt_claims

fileBP = Blueprint('app', __name__, url_prefix='/file')


@fileBP.route('/download', methods=['GET'])
@jwt_required
def download():
    """
    Allows a user to download a Picture from the server
    Parameters:
        type, String, the DocumentType of the object the picture is taken from. May be Picture, ProfilePicture or Badge
        id, String, the DocumentId of the document that contains the picture in the database
     if successful returns the image as attachment as id.png
     returns "invalid type or ID" if the given type was not among the options or and object with the ID did not exist
     NOTE requires a jwt access token in a Authorization header with value: Bearer <token>
    """
    type = request.args.get('type')
    id = request.args.get('id')
    # handling a Picture object
    if type == 'Picture':
        # asserting the id is valid
        if Picture.objects(id=id):
            # getting the picture from mongodb and reading the bytes
            pic = Picture.objects.get(id=id)
            raw = pic.picture.read()
            # converting bytes to image and sending it
            return send_file(io.BytesIO(raw),
                             attachment_filename=str(id) + '.png',
                             mimetype='image/png')
    # handling for other types is the same as for Picture
    elif type == 'ProfilePicture':
        if ProfilePicture.objects(id=id):
            pic = ProfilePicture.objects.get(id=id)
            raw = pic.picture.read()
            return send_file(io.BytesIO(raw),
                             attachment_filename=str(id) + '.png',
                             mimetype='image/png')

    elif type == 'Badge':
        if Badge.objects(id=id):
            badge = Badge.objects.get(id=id)
            raw = badge.picture.read()
            return send_file(io.BytesIO(raw),
                             attachment_filename=str(id) + '.png',
                             mimetype='image/png')
    return jsonify({"Error": "Invalid type or ID"})


@fileBP.route('/upload', methods=['POST'])
@jwt_required
def upload():
    """
    uploads a picture to the server and creates a new object to save it
    Parameters:
        type, String, DocumentType of the object to be saved. either Picture, ProfilePicture or Badge
        description, String, description used when creating a Picture or a badge
        name, String, name for a Badge
        id, String, id for a Badge. Has to be unique in the database.
        cost, Int, cost of a Badge
        :returns id of the created object if successful
        :returns Error: invalid type if type was not Badge Picture or ProfilePicture
        :returns Error: invalid Badge ID if the supplied badge id was already in use
    """
    if get_jwt_claims() != admin_claim:
        return jsonify({"Error": "Admin claim could not be verified"})
    type = request.args.get('type')
    # creates a new Picture in the database
    if type == 'Picture':
        description = request.args.get('description', default=None)
        pic = Picture(description=description)
        f = request.files['file']
        pic.picture.put(f, content_type='image/png')
        pic.save()
        return str(pic.id)
    # creates a new ProfilePicture in the database
    elif type == 'ProfilePicture':
        pic = ProfilePicture()
        f = request.files['file']
        pic.picture.put(f, content_type='image/png')
        pic.save()
        return str(pic.id)
    # creates a new Badge in the database
    elif type == 'Badge':
        id = request.args.get('id')
        if id is None or Badge.objects(id=id):
            return jsonify({"Error": "Badge ID exists"})
        description = request.args.get('description')
        name = request.args.get('name')
        cost = request.args.get('cost')
        badge = Badge(id=id, name=name, cost=cost, description=description)
        f = request.files['file']
        badge.picture.put(f, content_type='image/png')
        badge.save()
        return str(id)
    else:
        return jsonify({"Error": "Invalid type"})

# TODO: make this produce pdf
@fileBP.route('/questionpdf', methods=['GET'])
@jwt_required
def generatepdf():
    type = request.args.get('type')
    if type == 'question':
        id = request.args.get('id')
        if not Checkpoint.objects(id=id):
            return jsonify({"Error": "Invalid question ID"})
        question = Checkpoint.objects.get(id=id)
        if not Answer.objects(question=question):
            return jsonify({"Error": "No answers for this question"})
        answers = Answer.objects(question=question)
        file = io.BytesIO()
        file.write(str.encode("Exported answers for question: {} \n".format(question.id)))
        file.write(str.encode("Question:{} \n".format(question.question)))
        if isinstance(question, MultipleChoiceQuestion):
            file.write(str.encode("Possible answers: {} \n".format(question.possible_answers)))
            file.write(str.encode("Indices of the correct answers : {} \n".format(question.correct_answers)))
            file.write(str.encode("Maximum number of answers: {} \n".format(question.max_choices)))

        for answer in answers:
            file.write(str.encode("User: {} \n".format(answer.user.username)))
            file.write(str.encode("Answer: {} \n".format(answer.answer)))

        file.seek(0)
        return send_file(file, attachment_filename='report.txt', mimetype='text/plain')

    elif type == 'user':
        username = request.args.get('username')
        if not User.objects(username=username):
            return jsonify({"Error": "User does not exist"})
        user = User.objects.get(username=username)
        if not Answer.objects(user=user):
            return jsonify({"Error": "User has not submitted any answers"})
        file = io.BytesIO()
        file.write(str.encode("Exported answers for user: {} \n".format(user.username)))
        answers = Answer.objects(user=user)
        for answer in answers:
            question = answer.question
            file.write(str.encode("Question:{} \n".format(question.question)))
            if isinstance(question, MultipleChoiceQuestion):
                file.write(str.encode("Possible answers: {} \n".format(question.possible_answers)))
                file.write(str.encode("Indices of the correct answers : {} \n".format(question.correct_answers)))
                file.write(str.encode("Maximum number of answers: {} \n".format(question.max_choices)))
            file.write(str.encode("Answer: {} \n".format(answer.answer)))
        file.seek(0)
        return send_file(file, attachment_filename='report.txt', mimetype='text/plain')
    else:
        return jsonify({"Error": "Invalid type"})
