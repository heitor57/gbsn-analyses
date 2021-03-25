import numpy as np
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

parser = argparse.ArgumentParser()
parser.add_argument('--app',
                    type=str,
                    default='The Elder Scrolls III: Morrowind')
args = parser.parse_args()
# k,a = symbols('k a')
# fit_function = k**a
# lambda_fit_function = lambdify([k,a],fit_function)

db = utils.start_db()

g = igraph.Graph(directed=False)

vertexes = set()

appid = db.apps.find_one({'name': args.app})['appid']
uids = {
    review['author']['steamid']
    for review in db.reviews.find({'appid': appid}, {'author': 1})
}

uids = list(uids)

for user in tqdm(
        db.users.find(
            {
                "friendslist": {
                    "$exists": True
                },
                "steamid": {
                    '$in': uids
                }
            }, {
                '_id': 0,
                'steamid': 1
            }).batch_size(10000)):
    g.add_vertices(user['steamid'])
    vertexes.add(user['steamid'])

_buffer = []
_buffer_max_size = 10000
for user in tqdm(
        db.users.find(
            {
                "friendslist": {
                    "$exists": True
                },
                "steamid": {
                    '$in': uids
                }
            }, {
                '_id': 0,
                'steamid': 1,
                'friendslist': 1
            }).batch_size(3000)):
    try:
        _buffer.extend([(user['steamid'],i) for i in {friend['steamid'] for friend in user['friendslist']['friends']}.intersection(vertexes)])
        if len(_buffer) >= _buffer_max_size:
            g.add_edges(_buffer)
            _buffer=[]
    except Exception as e:
        print(e)
        pass

if len(_buffer) > 0:
    g.add_edges(_buffer)
    _buffer=[]

print("Graph created")

print(tabulate([[k, v] for k, v in graph.get_graph_infos(g).items()]))
print(g.summary())

fig = graph.plot_degree_distribution(g)
fig.savefig(f'degree_distribution_app_{args.app}.png')
fig = graph.plot_degree_distribution(g, type_='log')
fig.savefig(f'degree_distribution_log_app_{args.app}.png')



igraph.plot(g, target=f'users_graph_app_{args.app}.png',vertex_size=1)
# out.save()
