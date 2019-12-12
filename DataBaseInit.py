import pymongo
from pymongo import MongoClient

#############
# script to create the database locally for testing purposes/to port the layout to a new server
# database structure is documented in the repository
#############
# creating client and connection
client = MongoClient('localhost', 27017)

# client=pymongo.MongoClient()
# creating user database structure
# database users has subcollections for admins,regular users and a list of currently active codes users can use to get teacher rights
user_DB = client["user"]
users = user_DB["user"]
admins = user_DB["admin"]
upgrade_codes = user_DB["codes"]

# creating object database
# classification according to graphic in trello
# using naming to create sub sub collections.
# parent collections may not actually exist

object_DB = client["object"]
# here we're building imaginary subsub collections for the subcollection nature. the subcollection nature does not exists in the database as all the documents belong to one of the subsub collections
earth = object_DB["nature.earth"]
zoo = object_DB["nature.Zoo"]
# subsub collections for art and culture. see above
archeology = object_DB["culture.archeology"]
graphics = object_DB["culture.graphics"]
artpost1945 = object_DB["culture.post45"]
paintings = object_DB["culture.paintings"]
medieval = object_DB["culture.medieval"]
crafts = object_DB["culture.crafts"]

# creating database for tours
tour_DB = client["tour"]
# for the currently planned features we will only have one collection for all tours
# once public tours are available there will we collections for tours that are 'featured' or pending review
tours = tour_DB["tour"]

# creating dummy documents with representative layouts for the collections as mongoDB does not save collections without documents in them.
# as the layouts are representative they can be copied and edited to create new documents

# users template
# fields:
# username
# password
# rights are managed by membership in a collection
user = {"username": "test", "password": "test"}
users.insert_one(user)
admins.insert_one(user)


# testcode
code = {"code": "test"}
upgrade_codes.insert_one(code)

# tour template
# fields:
# name
# id : to join the session,randomly generated
# creator : reference to the user that created this tour
# participants : list of references to users that joined the tour
# objects : list of references to objects that are part of this tour
# tasks : list of questions and tasks for this tour
# answers : list of answers for each task per participant
tour = {"name": "test", "id": 123, "creator": "testcreator", "participants": ["testuser1", "testuser2"],
        "objects": ["obj1", "obj2"], "tasks": ["task1", "task2"], "answers": [{"user1": {"question1": "answer1"}}]}
tours.insert_one(tour)

# object models
# fields:
# name
# year
# creator
# category
####
# additional fields depending on object type
# for now only creating a template with generic fields
museum_object = {"name": "testname", "year": 2019, "creator": "me", "category": "painting"}
zoo.insert_one(museum_object)
earth.insert_one(museum_object)
medieval.insert_one(museum_object)
paintings.insert_one(museum_object)
graphics.insert_one(museum_object)
crafts.insert_one(museum_object)
archeology.insert_one(museum_object)
artpost1945.insert_one(museum_object)

print(client.list_database_names())
