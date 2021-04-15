
import numpy as np
import matplotlib.ticker as mtick
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
import cdlib
import cdlib.algorithms
import cdlib.evaluation
import networkx
import matplotlib.colors

parser = argparse.ArgumentParser()
parser.add_argument('--apps',
                    type=str,
                    default=['The Elder Scrolls III: Morrowind'],
                    nargs='*')
parser.add_argument('--giant', action='store_true')
args = parser.parse_args()

exec_name = "_".join(sorted(args.apps))
# k,a = symbols('k a')
# fit_function = k**a
# lambda_fit_function = lambdify([k,a],fit_function)

db = utils.start_db()

g = igraph.Graph(directed=False)


appsid = [i['appid'] for i in db.apps.find({'name': {'$in': args.apps}})]
uids = {
    review['author']['steamid']
    for review in db.reviews.find({'appid': {
        '$in': appsid
        }}, {'author': 1})
}
uids = list(uids)
game_counts = []
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
                # 'games': 1,
                'game_count': 1,
            }).batch_size(10000)):
    # print(user['game_count'])
    if user['game_count'] == None:
        user['game_count'] =0
    game_counts.append(user['game_count'])
    # g.add_vertices(user['steamid'])
    # vertexes.add(user['steamid'])

fig, ax = plt.subplots()
# print(game_counts)
# max_degree = max(g.degree())
# values, counts = np.unique(g.degree(), return_counts=True)
# counts = np.cumsum(counts / np.sum(counts))
# idxs = np.argsort(values)
# values = values[idxs]
# counts = counts[idxs]
ax.set_yscale('log')
ax.hist(game_counts, bins = int(180/5), color = 'blue',)
ax.set_ylabel('Quantity')
ax.set_xlabel('Number of games')
ax.set_title(f'{" ".join(args.apps)}')
fig.savefig(f'users_num_games_{exec_name}.png')


