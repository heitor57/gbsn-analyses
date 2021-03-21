from pymongo import MongoClient
import traceback
from steam import webapi
import utils
import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument('-apps', action='store_true')
# parser.add_argument('-reviews', action='store_true')
# args=parser.parse_args()

api = utils.create_api()

db = utils.start_db()


# if args.apps:
response = api.ISteamApps.GetAppList()
try:
    db.apps.insert_many(response['applist']['apps'])
except:
    traceback.print_exc()

# if args.reviews:
    # appsids = db.apps.find({'reviews':{"$exists":False}}, {'appid':1, '_id':0})
    

# for appid in apps_ids:
    # appid = appid['appid']
# api.call('appreviews')
# input()

