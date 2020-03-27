import os
import mongoengine
from flask_mongoengine import MongoEngine
from mongoengine import register_connection
from models.Badge import Badge
#from models.User import User
"""
Ingestion script for badges. Allows adding profile pictures to the database in bulk. Pictures are assumed to 
be in png format and located at data/badges relative to the location of this script.
Name and id for the badge are inferred from file name. Cost for now is fixed for bronze, silver, gold badge levels 
 
"""

# connect to database. assumes default port and no password
mongo = MongoEngine()
mongoengine.connect(host='localhost:27017')
register_connection("file", "file")
register_connection("user", "user")


def ingest_badges():
    # data path relative to this script
    file_path = 'data/badges'
    # iterating through the directory
    with os.scandir(file_path) as directory:
        for file in directory:
            # ignoring subdirectories
            if file.is_file():
                # ignoring non-png files. for first batch of badges different formats were provided.
                # for later additions if no png files are provided they will have to be converted to png
                if file.path.endswith('png'):
                    # get the actual data
                    # using with to ensure to file is closed
                    # mode HAS to be rb for mongoengine to be able to read the file
                    with open(file.path, 'rb') as picture:
                        # getting file name without extension
                        name = file.name[:-4]
                        # based on file name infer level and thus cost of the badge
                        if 'bronze' in name:
                            cost = 3
                        elif 'silber' in name:
                            cost = 10
                        elif 'gold' in name:
                            cost = 30
                        else:
                            cost = 100
                        # define document. needs these parameters to be created
                        badge = Badge(id=name, name=name, cost=cost)
                        # adding data to GridFS FileField
                        badge.picture.put(picture, content_type='image/png')
                        # saving
                        badge.save()
                        # reloading to get id
                        badge.reload()
                        #for user in User.objects.all():
                           # badges = user.badge_progress
                            #badges[str(id)] = 0
                            #user.update(set__badge_progress=badges)
                            #user.save()
                        # printing id for feedback on if the script is working.
                        print(badge.id)


ingest_badges()
