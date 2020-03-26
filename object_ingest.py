import os
import mongoengine
from models.MuseumObject import MuseumObject
import pandas as pd
from flask_mongoengine import MongoEngine
from mongoengine import register_connection
from models.Picture import Picture
"""
ingestion script for museum objects. allows adding objects located at /data/data.xls to the database
"""


mongo = MongoEngine()
mongoengine.connect(host='localhost:27017')
register_connection("user", "user")
register_connection("object", "object")
register_connection("tour", "tour")
register_connection("feedback", "feedback")
register_connection("file", "file")



def object_ingest(picture_dict):
    file_name = 'data/objects.xlsx'
    df = pd.read_excel(file_name, index_col=0)
    for idx, row in df.iterrows():
        museum_object = MuseumObject(object_id=str(row['Inventarnummer']), category=row['Abteilung'],
                                     sub_category=row['Sammlungsbereich'], title=row['Titel'])
        museum_object.save()
        # setting the obvious single value fields
        museum_object.update(set__description=str(row['Objektbeschreibung']))
        museum_object.update(set__additional_information=str(row['additional']))
        # then doing the more complicated list fields

        inter = row['Interdisciplinary']
        inter = inter.strip()
        museum_object.update(set__interdisciplinary_context=inter)

        year = str(row['Datierung'])
        year = year.replace(u'\xa0', u'')
        year = year.strip()
        museum_object.update(set__year=year)

        art_type = str(row['Objektgattung'])
        art_type = art_type.strip()
        museum_object.update(set__art_type=art_type)

        creator = str(row['Hersteller'])
        creator = creator.replace(u'\xa0', u' ')
        creator = creator.strip()
        museum_object.update(set__creator=creator)

        material = str(row['Material'])
        material = material.strip()
        museum_object.update(set__material=material)

        size = str(row['Size'])
        size = size.strip()
        museum_object.update(set__size_=size)

        location = str(row['Verortung'])
        location = location.strip()
        museum_object.update(set__location=location)

        pictures = []
        for picture_name in [name.strip() for name in row['Bild'].replace('\n', '').split(',')]:
            pid = picture_dict[picture_name]
            pic = Picture.objects.get(id=pid)
            pictures.append(pic)
        museum_object.update(set__picture=pictures)
        museum_object.save()


def picture_ingest():
    picture_directory = 'data/pictures'
    id_dict = {}
    with os.scandir(picture_directory) as directory:
        for file in directory:
            if file.is_file():
                if file.path.endswith('jpg'):
                    with open(file.path, 'rb') as picture:
                        pic = Picture()
                        pic.picture.put(picture, content_type='image/jpeg')
                        pic.save()
                        pic.reload()
                        id_dict[str(file.name)] = str(pic.id)

    return id_dict


picture_dict = picture_ingest()
object_ingest(picture_dict)

