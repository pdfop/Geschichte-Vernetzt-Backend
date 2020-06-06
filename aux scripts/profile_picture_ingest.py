import os
import mongoengine
from flask_mongoengine import MongoEngine
from mongoengine import register_connection
from models.ProfilePicture import ProfilePicture
"""
Ingestion script for profile pictures. Allows adding profile pictures to the database in bulk. Pictures are assumed to 
be in jpg format and located at data/profilepictures relative to the location of this script. 
"""

# connect to database. assumes default port and no password
mongo = MongoEngine()
mongoengine.connect(host='localhost:27017')
register_connection("file", "file")


def ingest_profile_pictures():
    # data path relative to this script
    file_path = 'data/profilepictures'
    # iterating through the directory
    with os.scandir(file_path) as directory:
        for file in directory:
            # ignoring subdirectories
            if file.is_file():
                # ignoring non-jpg files. convert to jpg before running
                if file.path.endswith('jpg'):
                    # get the actual data
                    # using with to ensure to file is closed
                    # mode HAS to be rb for mongoengine to be able to read the file
                    with open(file.path, 'rb') as picture:
                        # defining document
                        pic = ProfilePicture()
                        # adding data to GridFS FileField
                        pic.picture.put(picture, content_type='image/jpeg')
                        # saving
                        pic.save()
                        # reloading to get id
                        pic.reload()
                        # printing id for feedback on if the script is working.
                        print(pic.id)


ingest_profile_pictures()
