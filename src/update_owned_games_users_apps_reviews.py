import numpy as np
import requests
import argparse
import utils
from scipy import *
import igraph
from tqdm import tqdm
from tabulate import tabulate
import matplotlib.pyplot as plt
import scipy.optimize
from sympy import *
import graph

import urllib.parse
parser = argparse.ArgumentParser()
parser.add_argument('--apps',
                    type=str,
                    default=['The Elder Scrolls III: Morrowind'],
                    nargs='*')
parser.add_argument('--max_num_iterations',
                    type=int,
                    help='Maximum number of iterations to do at crawling',
                    default=30000)
args = parser.parse_args()

api = utils.create_api()

db = utils.start_db()

appsid = [i['appid'] for i in db.apps.find({'name': {'$in': args.apps}})]
uids = {
    review['author']['steamid']
    for review in db.reviews.find({'appid': {
        '$in': appsid
    }}, {'author': 1})
}

users = db.users.find(
    {
        'games': {
            "$exists": False,
        },
        "steamid": {
            '$in': list(uids)
        }
    }, {
        'steamid': 1,
        '_id': 0
    })
num_users_to_update = users.count()
print('Users to update', num_users_to_update)

users.rewind()
num_iterations = 0
for user in users:
    print(num_users_to_update,num_iterations)
    response = api.call('IPlayerService.GetOwnedGames',
                        steamid=user['steamid'],
                        include_played_free_games=True,
                        include_appinfo=True,
                        include_free_sub=True,
                        appids_filter=None
                        )
    # print(f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key=77D74BF982D2059A8D78165DBEA76664&format=json&steamid={urllib.parse.quote(user['steamid'])}&include_appinfo=1&include_played_free_games=1&include_free_sub=1")
    # response = requests.get(f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key=77D74BF982D2059A8D78165DBEA76664&format=json&steamid={urllib.parse.quote(user['steamid'])}&include_appinfo=1&include_played_free_games=1&include_free_sub=1").json()
    data = dict()
    fields = ['games','game_count']
    for field in fields:
        data[field] = None
        if field in response['response']:
            data[field] = response['response'][field]

    # print(data)
    db.users.update_one({"steamid": user['steamid']}, {"$set": data})
    num_users_to_update -= 1
    num_iterations += 1
    if num_iterations >= args.max_num_iterations:
        break
