from pymongo import MongoClient
import pymongo
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
print(app['name'],appid)
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
request_parameters = {
    'json': '1',
    'language': 'all',  
    'filter': 'recent',
    'review_type': 'all', 
    'purchase_type': 'all', 
    'num_per_page': '100',  
    'cursor':'*'
}


is_end = False
# num_per_page = 100
while not is_end:
    try:
        s = f'https://store.steampowered.com/appreviews/{appid}'
        response = requests.get(url=s,params=request_parameters)
        print(response.url)
        response = response.json()
        if request_parameters['cursor'] == response["cursor"]:
            print("Loop, END")
            break
        request_parameters['cursor'] = response["cursor"]
        # is_end = not (response['query_summary']['num_reviews'] == num_per_page)
        # print(response)
        for review in response['reviews']:
            review['appid'] = appid
        db.reviews.insert_many(response['reviews'],ordered=False)
    except pymongo.errors.BulkWriteError as e:
        print("Bulk write error")

# api.call('appreviews')
# input()
