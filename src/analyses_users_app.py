import numpy as np
import matplotlib.ticker as mtick
import argparse
import utils
from scipy import *
import os.path
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

MDIR = 'data/'

parser = argparse.ArgumentParser()
parser.add_argument('--apps',
                    type=str,
                    default=['The Elder Scrolls III: Morrowind'],
                    nargs='*')
parser.add_argument('--giant', action='store_true')
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
    for review in db.reviews.find({'appid': {
        '$in': appsid
    }}, {'author': 1})
}

uids = list(uids)

# name_id_map = dict()
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
                'games': 1,
            }).batch_size(10000)):
    g.add_vertices(user['steamid'])
    vertexes.add(user['steamid'])
    g.vs[-1]["games"] = []
    if user['games'] != None:
        g.vs[-1][i['appid'] for i in user['games']]

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
        _buffer.extend([(user['steamid'], i) for i in {
            friend['steamid'] for friend in user['friendslist']['friends']
        }.intersection(vertexes)])
        if len(_buffer) >= _buffer_max_size:
            g.add_edges(_buffer)
            _buffer = []
    except Exception as e:
        print(e)
        pass

if len(_buffer) > 0:
    g.add_edges(_buffer)
    _buffer = []

del(g.vs['name'])
exec_name = "_".join(sorted(args.apps)) + ('_giant' if args.giant else '')
# print(exec_name)

# print(os.path.join(MDIR,exec_name+'.txt'))
log = open(os.path.join(MDIR,exec_name+'.txt'),'w+')
log.write("Graph created\n")
g = g.simplify()

if args.giant:
    g = g.components(mode='weak').giant()


log.write(tabulate([[k, v] for k, v in graph.get_graph_infos(g).items()]))
log.write('\n')
log.write(tabulate([[k, v] for k, v in graph.get_graph_infos(g).items()], tablefmt="latex"))
log.write('\n')

# log.write(help(g.summary))
log.write(g.summary())
log.write('\n')

# log.write(help(g.components))
# log.write(giant.summary())
# igraph.plot(giant, target=f'users_graph_app_{exec_name}.png',vertex_size=0.8,edge_width=0.8)

# raise SystemExit

fig = graph.plot_degree_distribution(g)
fname = f'degree_distribution_app_{exec_name}.png'
fig.savefig(os.path.join(MDIR,fname))
fig = graph.plot_degree_distribution(g, type_='log')
fname = f'degree_distribution_log_app_{exec_name}.png'
fig.savefig(os.path.join(MDIR,fname))
# fig.savefig()
# fig = graph.plot_degree_distribution(g, type_='log')

# popt, pcov= scipy.optimize.curve_fit(fit_function,xdata=values,ydata=counts)
# fitted_function = fit_function.subs(a, UnevaluatedExpr(popt[0]))
# fitted_function = lambdify(k,fitted_function)
# fitted_function = lambda k: k**popt[0]

# line = ax.plot(values,list(map(lambda k: fit_function(k,*popt),values)),color='k')

# s= f'Fitted line (${popt[1]:.3f}k^{{{popt[0]:.3f}}}$)'
# log.write(s)
# ax.legend([s,'Collected data'])

# subgraph_vs = (g.vs(name=m)[0].index for m in members)

# log.write(communities.sizes())

fig, ax = plt.subplots()
# max_degree = max(g.degree())
values, counts = np.unique(g.degree(), return_counts=True)
counts = np.cumsum(counts / np.sum(counts))
idxs = np.argsort(values)
values = values[idxs]
counts = counts[idxs]
# if type_=='log':
# ax.set_xscale('log')
# ax.set_yscale('log')

ax.scatter(values, counts, facecolors='none', edgecolors='k')
ax.set_xlabel('x')
ax.set_ylabel('Probability(Degree$>=$x)')
fname = f'degree_ccdf_distribution_log_app_{exec_name}.png'
fig.savefig(os.path.join(MDIR,fname))



netg = networkx.Graph(g.get_edgelist())
partition = cdlib.algorithms.louvain(netg, resolution=1.0, randomize=False)

mod = cdlib.evaluation.newman_girvan_modularity(netg, partition)
del netg
log.write(repr(mod)+'\n')


fig, ax = plt.subplots()
values = np.sort([len(community) for community in partition.communities])
x = list(range(len(values)))
y = np.cumsum(values)/len(g.vs)
# 
# ax.plot(x,y,color='k')
ax.scatter(x,y,facecolors='red', edgecolors='k')
ax.set_ylabel('Percentage of users cumulated')
ax.set_xlabel('Community')
ax.set_title(f'{exec_name}')
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
fname = f'communities_num_app_{exec_name}.png'
fig.savefig(os.path.join(MDIR,fname))

# log.write(partition.communities)
# communities=g.community_fastgreedy()
# log.write(communities.membership())
# log.write(communities.sizes())
# log.write(type(communities))
num_communities = len(partition.communities)
colors = [matplotlib.colors.to_hex(plt.get_cmap('gist_rainbow')(i/(num_communities-1))) for i in range(num_communities)]
# mark_groups = {vertexes:color for color, vertexes in zip(colors,partition.communities)}
# log.write(del g.vs['name'])
# g.delete_vertex_attr('name')

# partitions_sizes = list(map(len,partition.communities))

# communities = [x for _, x in reversed(sorted(zip(partitions_sizes, partition.communities)))]

# top_partitions = 5
# for i in range(top_partitions):
    # for db.users.find({''})
    # communities[i]

for color, vertexes in zip(colors, partition.communities):
    # if color == None:
        # log.write("ewqokewqk")
    # log.write(color)
    g.vs[vertexes]['color'] = color
    # log.write(g.vs[vertexes]['color'])

fname = f'users_graph_app_{exec_name}.png'
igraph.plot(g,
            target=os.path.join(MDIR,fname),
            vertex_size=2.8,
            edge_width=0.8,
            mark_groups={
                tuple(vertexes): color
                for color, vertexes in zip(colors, partition.communities)
            }
            )



# subgraph_vs = g.vs.select(lambda vertex: vertex.degree() > 5)
# g = g.subgraph(subgraph_vs)
# subgraph_vs = g.vs.select(lambda vertex: vertex.degree() > 5)
# g = g.subgraph(subgraph_vs)
# g = g.simplify()

# i = g.community_fastgreedy().as_clustering(5)

# # log.write(len(i))
# colors = ["#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00"]
# g.vs['color'] = [None]
# for clid, cluster in enumerate(i):
# for member in cluster:
# g.vs[member]['color'] = colors[clid]
# g.vs['frame_width'] = 0
# igraph.plot(g,target=f'users_graph_app_communities_{exec_name}.png')

# subgraph_vs = g.vs.select(lambda vertex: vertex.degree() > 0)

# g = g.subgraph(subgraph_vs)
# g = g.simplify()
# # log.write(np.min(g.degree()))
# # log.write(np.min(g.degree()))
# # g.vs['label'] = g.degree()
# igraph.plot(g, target=f'users_graph_app_wout_0{exec_name}.png',vertex_size=2.8,edge_width=2.0,
# # layout=g.layout('drl')
# )
log.close()
