from pymongo import MongoClient

from tohsaka import settings

client = MongoClient(settings.DB_HOST+':'+settings.DB_PORT)
db = client[settings.DB_NAME]


def post(board, author, resto, comment, image, passhash):
    result = db.posts.insert_one({
        "board": board,
        "author": author,
        "resto": resto,
        "comment": comment,
        "image": image,
        "password": passhash
    })
    return str(result.inserted_id)


