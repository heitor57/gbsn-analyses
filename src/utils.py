from steam import webapi
import time
from pymongo import MongoClient

def get_user_data(api,user_id):
    try:
        response = api.call('ISteamUser.GetFriendList',
                            relationship='friend',
                            steamid=user_id)
        user_data = {}
        user_data.update(response)
        user_data['steamid'] = user_id
        return user_data
    except Exception as e:
        print(e)
        return {'steamid': user_id, 'invalid': True}

def start_db():
    client = MongoClient("mongodb://localhost:27017")
    db = client.gbsn
    return db

def create_api():
    key = open('key.txt').read().rstrip()
    api = webapi.WebAPI(key)
    return api
