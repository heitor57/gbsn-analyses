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
parser.add_argument('--apps',
                    type=str,
                    default=['The Elder Scrolls III: Morrowind'],nargs='*')
args = parser.parse_args()
# k,a = symbols('k a')
# fit_function = k**a
# lambda_fit_function = lambdify([k,a],fit_function)

db = utils.start_db()

g = igraph.Graph(directed=False)

vertexes = set()

appsid = [i['appid'] for i in db.apps.find({'name': {'$in': args.apps}})]
uids = {
    review['author']['steamid']
    for review in db.reviews.find({'appid': {'$in': appsid}}, {'author': 1})
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

g = g.simplify()

print(tabulate([[k, v] for k, v in graph.get_graph_infos(g).items()]))
print(g.summary())

exec_name = "_".join(sorted(args.apps))
fig = graph.plot_degree_distribution(g)
fig.savefig(f'degree_distribution_app_{exec_name}.png')
fig = graph.plot_degree_distribution(g, type_='log')
fig.savefig(f'degree_distribution_log_app_{exec_name}.png')

# subgraph_vs = (g.vs(name=m)[0].index for m in members)

# communities=g.community_fastgreedy()
# print(communities.membership())
# print(communities.sizes())

igraph.plot(g, target=f'users_graph_app_{exec_name}.png',vertex_size=0.8,edge_width=0.8)


# subgraph_vs = g.vs.select(lambda vertex: vertex.degree() > 5)
# g = g.subgraph(subgraph_vs)
# subgraph_vs = g.vs.select(lambda vertex: vertex.degree() > 5)
# g = g.subgraph(subgraph_vs)
# g = g.simplify()

i = g.community_fastgreedy().as_clustering(5)

# print(len(i))
colors = ["#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00"]
g.vs['color'] = [None]
for clid, cluster in enumerate(i):
    for member in cluster:
        g.vs[member]['color'] = colors[clid]
g.vs['frame_width'] = 0
igraph.plot(g,target=f'users_graph_app_communities_{exec_name}.png')


# subgraph_vs = g.vs.select(lambda vertex: vertex.degree() > 0)

# g = g.subgraph(subgraph_vs)
# g = g.simplify()
# # print(np.min(g.degree()))
# # print(np.min(g.degree()))
# # g.vs['label'] = g.degree()
# igraph.plot(g, target=f'users_graph_app_wout_0{exec_name}.png',vertex_size=2.8,edge_width=2.0,
        # # layout=g.layout('drl')
        # )
