from flask_mongoengine import MongoEngine
from mongoengine import register_connection

""" Defines the mongoengine connection to the mongodb database. 
    New databases have to be added here.
    These are only the databases. New collections to existing databases can be freely added. 
"""
mongo = MongoEngine()
register_connection("user", "user")
register_connection("object", "object")
register_connection("tour", "tour")
register_connection("feedback", "feedback")
register_connection("file", "file")

