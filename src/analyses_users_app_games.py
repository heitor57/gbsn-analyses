
import matplotlib.dates as mdates
import numpy as np
import matplotlib.ticker as mtick
import argparse
import utils
from scipy import *
import igraph
from tqdm import tqdm
from tabulate import tabulate
import os
import os.path
import matplotlib.pyplot as plt
import scipy.optimize
from sympy import *
import graph
import cdlib
import cdlib.algorithms
import cdlib.evaluation
import networkx
import matplotlib.colors
MDIR = 'data/'

parser = argparse.ArgumentParser()
parser.add_argument('--apps',
                    type=str,
                    default=['The Elder Scrolls III: Morrowind'],
                    nargs='*')
parser.add_argument('--giant', action='store_true')
args = parser.parse_args()

exec_name = "_".join(sorted(args.apps)) + ('_giant' if args.giant else '')
# k,a = symbols('k a')
# fit_function = k**a
# lambda_fit_function = lambdify([k,a],fit_function)

db = utils.start_db()


g = igraph.Graph(directed=False)

apps = {i['appid']:i for i in db.apps.find()}
# print(apps)

appsid = [i['appid'] for i in db.apps.find({'name': {'$in': args.apps}})]
uids = {
    review['author']['steamid']
    for review in db.reviews.find({'appid': {
        '$in': appsid
        }}, {'author': 1})
}
uids = list(uids)
game_counts = []
prices_count = []
for user in tqdm(
        db.users.find(
            {
                "friendslist": {
                    "$exists": True
                },
                "steamid": {
                    '$in': uids
                },
                'games':{'$exists':True}
            }, {
                '_id': 0,
                # 'steamid': 1,
                'games': 1,
                'game_count': 1,
            }).batch_size(10000)):
    # print(user['game_count'])
    if user['game_count'] == None:
        user['game_count'] = 0
    game_counts.append(user['game_count'])

    # games.extend([i['appid'] for i in user['games']])

    if user['games'] != None:
        for i in user['games']:
            if i['appid'] in apps:
                # print(apps[i['appid']]['price'])
                if apps[i['appid']]['price'] != None:
                    prices_count.append(int(apps[i['appid']]['price'])/100)
    # games.extend(user['games'])
    # g.add_vertices(user['steamid'])
    # vertexes.add(user['steamid'])

# list(map(lambda x: apps[x]['price'],games))

# print(prices_count)
fig, ax = plt.subplots()
ax.set_yscale('log')
ax.hist(game_counts, bins = int(180/5), color = 'blue',)
ax.set_ylabel('Quantity')
ax.set_xlabel('Number of games')
# ax.set_title(f'{" ".join(args.apps)}')

fname = f'users_num_games_{exec_name}.png'
fig.savefig(os.path.join(MDIR,fname))


fig, ax = plt.subplots()
# ax.set_yscale('log')
ax.hist(prices_count, bins = int(180/5), color = 'blue',)
ax.set_ylabel('Frequência de preço')
ax.set_xlabel('Preço')
fname = f'users_num_prices_{exec_name}.png'
fig.savefig(os.path.join(MDIR,fname))


fig, ax = plt.subplots()
# ax.set_yscale('log')
ax.hist(prices_count, bins = int(180/5), color = 'blue',)
ax.set_ylabel('Frequência de preço')
ax.set_xlabel('Preço')
fname = f'users_num_prices_{exec_name}.png'
fig.savefig(os.path.join(MDIR,fname))

# fig, ax = plt.subplots()

# locator = mdates.AutoDateLocator()
# ax.xaxis.set_major_locator(locator)
# ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))


