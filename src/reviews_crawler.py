from pymongo import MongoClient
import urllib
import traceback
import requests
import time
from steam import webapi
import utils
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--app',
                    type=str,
                    default='The Elder Scrolls III: Morrowind')
args = parser.parse_args()

db = utils.start_db()

# appsids = db.apps.find({'reviews':{"$exists":False}}, {'appid':1, '_id':0})
app = db.apps.find_one({'name': args.app})

appid = app['appid']
print(app['name'])
# appid = '1220140'
cursor = '*'
# s = f'https://store.steampowered.com/appreviews/{appid}?json=1&cursor=*'
# print(s)
# response = requests.get(url=s)
# response = response.json()
# for review in response['reviews']:
    # review['appid'] = appid
# try:
    # db.reviews.insert_many(response['reviews'])
# except:
    # traceback.print_exc()
is_end = False

while not is_end:
    print(cursor)
    time.sleep(5)
    try:
        s = f'https://store.steampowered.com/appreviews/{appid}?json=1&cursor={cursor}'
        print(s)
        response = requests.get(url=s)
        response = response.json()
        cursor = urllib.parse.quote(response["cursor"])
        is_end = not (response['query_summary']['num_reviews'] == 20)
        # print(response)
        for review in response['reviews']:
            review['appid'] = appid
        db.reviews.insert_many(response['reviews'])
    except Exception as e:
        print("Error",e)
        # traceback.print_exc()

# api.call('appreviews')
# input()
