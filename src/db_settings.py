from steam import webapi
import time
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client.gbsn

db.users.create_index([('steamid', pymongo.ASCENDING)],unique=True)
db.apps.create_index([('appid', pymongo.ASCENDING)],unique=True)
db.reviews.create_index([('recommendationid', pymongo.ASCENDING)],unique=True)

