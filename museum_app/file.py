import io
from flask import Blueprint, send_file, request
from models.Answer import Answer
from models.Checkpoint import Checkpoint
from models.Picture import Picture
from models.ProfilePicture import ProfilePicture
from models.Badge import Badge
from models.User import User
import tempfile

fileBP = Blueprint('app', __name__, url_prefix='/file')


@fileBP.route('/download', methods=['GET'])
def download():
    type = request.args.get('type')
    id = request.args.get('id')
    if type == 'Picture':
        pic = Picture.objects.get(id=id)
        raw = pic.picture.read()
        return send_file(io.BytesIO(raw),
                         attachment_filename=str(id) + '.png',
                         mimetype='image/png')

    elif type == 'ProfilePicture':
        pic = ProfilePicture.objects.get(id=id)
        raw = pic.picture.read()
        return send_file(io.BytesIO(raw),
                         attachment_filename=str(id) + '.png',
                         mimetype='image/png')

    elif type == 'Badge':
        pic = Badge.objects.get(id=id)
        raw = pic.picture.read()
        return send_file(io.BytesIO(raw),
                         attachment_filename=str(id) + '.png',
                         mimetype='image/png')
    return "wrong"


@fileBP.route('/upload', methods=['POST'])
def upload():
    type = request.args.get('type')
    if type == 'Picture':
        description = request.args.get('description', default=None)
        pic = Picture(description=description)
        f = request.files['file']
        pic.picture.put(f, content_type='image/png')
        pic.save()
        return str(pic.id)
    elif type == 'ProfilePicture':
        pic = ProfilePicture()
        f = request.files['file']
        pic.picture.put(f, content_type='image/png')
        pic.save()
        return str(pic.id)
    elif type == 'Badge':
        description = request.args.get('description')
        name = request.args.get('name')
        id = request.args.get('id')
        cost = request.args.get('cost')
        badge = Badge(id=id, name=name, cost=cost)
        f = request.files['file']
        badge.picture.put(f, content_type='image/png')
        badge.save()
        return str(id)
    else:
        return "wrong"


@fileBP.route('/questionpdf', methods=['GET'])
def generatepdf():
    type = request.args.get('type')
    if type == 'question':
        id = request.args.get('id')

        question = Checkpoint.objects.get(id=id)
        answers = Answer.objects(question=question)

        file = io.BytesIO()
        file.write(str.encode("Exported answers for question: {} \n".format(question.id)))
        file.write(str.encode("Question:{} \n".format(question.question)))

        for answer in answers:
            file.write(str.encode("User: {} \n".format(answer.user.username)))
            file.write(str.encode("Answer: {} \n".format(answer.answer)))

        file.seek(0)
        return send_file(file, attachment_filename='report.txt', mimetype='text/plain')

    elif type == 'user':
        username = request.args.get('username')
        user = User.objects.get(username=username)
        answers = Answer.objects(user=user)
        return "wip"
    else:
        return "wrong"
