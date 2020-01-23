from flask_mongoengine import MongoEngine
from mongoengine import register_connection

mongo = MongoEngine()
register_connection("user", "user")
register_connection("object", "object")
register_connection("tour", "tour")
register_connection("feedback", "feedback")

