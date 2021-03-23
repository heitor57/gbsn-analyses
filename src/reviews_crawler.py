from pymongo import MongoClient
import urllib
import traceback
import requests
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
s = f'https://store.steampowered.com/appreviews/{appid}?json=1&cursor=*&day_range=9223372036854775807'
print(s)
response = requests.get(url=s)
response = response.json()
for review in response['reviews']:
    review['appid'] = appid
try:
    db.reviews.insert_many(response['reviews'])
except:
    traceback.print_exc()

while response['query_summary']['num_reviews'] == 20:
    try:
        s = f'https://store.steampowered.com/appreviews/{appid}?json=1&cursor={urllib.parse.quote(response["cursor"])}&day_range=9223372036854775807'
        print(s)
        response = requests.get(url=s)
        response = response.json()
        # print(response)
        for review in response['reviews']:
            review['appid'] = appid

        db.reviews.insert_many(response['reviews'])
    except:
        traceback.print_exc()

# api.call('appreviews')
# input()
