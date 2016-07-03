import pymongo
from pymongo import MongoClient
import bson.objectid
import datetime
import time
import os

from tohsaka import settings

client = MongoClient(settings.DB_HOST+':'+settings.DB_PORT)
db = client[settings.DB_NAME]


def post(board, author, resto, comment, image, passhash):
    if image is None:
        result = db.posts.insert_one({
            "board": board,
            "author": author,
            "resto": resto,
            "comment": comment,
            "image": image,
            "password": passhash
        })
    else:
        result = db.posts.insert_one({
            "board": board,
            "author": author,
            "resto": resto,
            "comment": comment,
            "image": image[0],
            "thumbnail": image[1],
            "original": image[2],
            "password": passhash
        })
    return str(result.inserted_id)


def get_threads(board, page):
    cursor = db.posts.find({
        'resto': 0,
        'board': board
    }).sort('bumped', pymongo.DESCENDING).skip((int(page)-1)*settings.THREADS_PER_PAGE).limit(settings.THREADS_PER_PAGE)
    threads = [{
                   **thread,
                   'replies': [reply for reply in db.posts.find({
                                'resto': thread['_id']
                                }).sort('_id', pymongo.DESCENDING).limit(settings.PREVIEW_REPLIES)]
               } for thread in cursor]
    return threads


def upload_file(file):
    try:
        xtindex = file.filename.rindex('.')
    except:
        return None
    filext = file.filename[xtindex-len(file.filename):]
    timestamp = str(time.time()).replace('.', '')
    finalfilepath = settings.IMG_PATH+timestamp+filext
    os.makedirs(os.path.dirname(finalfilepath), exist_ok=True)
    fout = open(finalfilepath, 'wb')
    fout.write(file.file.read())
    fout.close()
    return timestamp+filext, timestamp+'s'+filext, file.filename


def register_custom_json(renderer):
    def objectid_renderer(oid, request):
        return str(oid)
    renderer.add_adapter(bson.objectid.ObjectId, objectid_renderer)

    def datetime_renderer(dt, request):
        return dt.isoformat()
    renderer.add_adapter(datetime.datetime, datetime_renderer)