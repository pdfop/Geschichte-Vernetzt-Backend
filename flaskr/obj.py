from models.MuseumObject import MuseumObject
from flask import Blueprint
from .extensions import mongo
"""
Subapp to handle object management
creates,edits and retrieves objects from the database 
creation and edit requests have to refer to the collection the object is in by calling /category/subcategory
searches may omit this structure 
"""
obj = Blueprint('obj', __name__, template_folder='models', url_prefix='/object')

@obj.route('/')
def landing():
    return "Landing Page. Please use /create,/find or /update"
@obj.route('/create/<category>/<subcategory>/<name>')
def createObject(category, subcategory, name):
    museumObject = MuseumObject(name)
    scat = category+"."+subcategory
    collection = mongo.cx["object"][scat]
    if name not in collection.find({"name": name}):
        collection.insert_one(museumObject)
    else:
        return "Object exists in this Category with id {}. Please use /obj/update/<id>".format(123)

@obj.route('/find/<category>/<subcategory>/<name>')
def findObject(category, subcategory, name):
    scat = category + "." + subcategory
    collection = mongo.cx["object"][scat]
    result = collection.findOne({"name": name})
    return result

#TODO: Handle different types of objects with different fields
#TODO: General find function management (return all found?)
