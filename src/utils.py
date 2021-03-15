from steam import webapi
import time
from pymongo import MongoClient
def start_db():
    client = MongoClient("mongodb://localhost:27017")
    db = client.gbsn
    return db

def create_api():
    key = open('key.txt').read().rstrip()
    api = webapi.WebAPI(key)
    return api
