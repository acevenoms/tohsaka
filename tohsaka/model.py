import pymongo
from pymongo import MongoClient
import bson.objectid
from bson.objectid import ObjectId
from datetime import datetime
from datetime import timezone
from wand.image import Image
import time
import os

from tohsaka import settings

client = MongoClient(settings.DB_HOST+':'+settings.DB_PORT)
db = client[settings.DB_NAME]


def post(resto, board, author, email, passhash, comment, image, sticky):
    postObject = {
            "resto": resto,
            "board": board,
            "author": author,
            "email": email,
            "password": passhash,
            "comment": comment,
            "sticky": sticky,
            "bumped": datetime.now(timezone.utc)
        }
    if image is None:
        postObject["image"] = None
        postObject["thumbnail"] = None
        postObject["original"] = None
        postObject["info"] = None
    else:
        postObject["image"] = image[0]
        postObject["thumbnail"] = image[1]
        postObject["original"] = image[2]
        postObject["info"] = image[3]

    if resto != 0:
        try:
            threadId = ObjectId(resto)
            postObject['resto'] = threadId
        except:
            return {'code': 1, 'message': 'Invalid thread ID: ' + str(resto)}
        if email != 'sage': # sage goes only in the email field
            numReplies = db.posts.count({"resto": threadId})
            if numReplies < settings.REPLY_LIMIT:
                # bump
                result = db.posts.update_one({"_id": threadId}, {
                    "$currentDate": {"bumped": True}
                })
                if result.matched_count < 1:
                    return {'code': 2, 'message': 'Thread does not exist'}
                # Don't forget to ACTUALLY INSERT THE POST YA DINGUS
                result = db.posts.insert_one(postObject)
                if result.acknowledged is False:
                    return {'code': 3, 'message': 'Failed to reply'}
                result = threadId
    else:
        if image is None:
            return {'code': 4, 'message': 'You must post an image to start a thread'}
        else:
            result = db.posts.insert_one(postObject).inserted_id

    return {'code': 0, 'board': board, 'thread': str(result)}


def get_threads(board, page):
    cursor = db.posts.find({
        'resto': 0,
        'board': board
    }).sort('bumped', pymongo.DESCENDING).skip((int(page)-1)*settings.THREADS_PER_PAGE).limit(settings.THREADS_PER_PAGE)
    threads = [{**thread, 'timestamp': thread['_id'].generation_time} for thread in cursor]
    replies = {}
    for thread in threads:
        replies[str(thread['_id'])] = [{**reply, 'timestamp': reply['_id'].generation_time} for reply in db.posts.find({
                                    'resto': thread['_id']
                                    }).sort('_id', pymongo.DESCENDING).limit(settings.PREVIEW_REPLIES)]
    return {'threads': threads, 'replies': replies}


def get_single_thread(board, thread):
    cursor = db.posts.find({
        '_id': ObjectId(thread),
        'board': board
    }).limit(1)
    threads = [{**thread, 'timestamp': thread['_id'].generation_time} for thread in cursor]
    replies = {}
    for thread in threads:
        replies[str(thread['_id'])] = [{**reply, 'timestamp': reply['_id'].generation_time} for reply in db.posts.find({
            'resto': thread['_id']
        }).sort('_id', pymongo.ASCENDING)]
    return {'threads': threads, 'replies': replies}

def upload_file(file):
    try:
        xtindex = file.filename.rindex('.')
    except:
        return None
    filext = file.filename[xtindex-len(file.filename):]
    timestamp = str(time.time()).replace('.', '')
    finalfilepath = settings.IMG_PATH+timestamp+filext
    finalthumbpath = settings.IMG_PATH+timestamp+settings.THUMB_EXTENSION
    os.makedirs(os.path.dirname(finalfilepath), exist_ok=True)
    image = Image(blob=file.file.read())
    fileinfo = {
        'bytes': file.bytes_read,
        'width': image.width,
        'height': image.height
    }
    image.save(filename=finalfilepath)
    thumbSize = calculateThumbDimensions(image.width, image.height)
    if len(image.sequence) > 1:
        image = Image(image.sequence[0])
        image = image.convert('png')
    image.resize(thumbSize[0], thumbSize[1], 'box')
    image.save(filename=finalthumbpath)
    # fout = open(finalfilepath, 'wb')
    # fout.write(file.file.read())
    # fout.close()

    return timestamp+filext, timestamp+settings.THUMB_EXTENSION, file.filename, fileinfo


def calculateThumbDimensions(width,height):
    largerDim = width if width > height else height
    ratio = settings.THUMB_SIZE / largerDim
    return round(width*ratio), round(height*ratio)


def register_custom_json(renderer):
    def objectid_renderer(oid, request):
        return str(oid)
    renderer.add_adapter(bson.objectid.ObjectId, objectid_renderer)

    def datetime_renderer(dt, request):
        return dt.isoformat()
    renderer.add_adapter(datetime, datetime_renderer)