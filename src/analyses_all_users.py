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

fit_function = lambda k,a: k**a

db = utils.start_db()

g = igraph.Graph(directed=False)

vertexes = set()
for user in tqdm(db.users.find({"friendslist": {
            "$exists": True
            }},{'_id':0,'steamid':1}).batch_size(10000).limit(100000)):
    g.add_vertices(user['steamid'])
    vertexes.add(user['steamid'])
 

_buffer = []
_buffer_max_size = 10000
for user in tqdm(db.users.find({"friendslist": {
            "$exists": True
            }},{'_id':0,'steamid':1,'friendslist':1}).batch_size(10000).limit(100000)):
    # print(user['friendslist']['friends'])
    try:
        _buffer.extend([(user['steamid'],i) for i in {friend['steamid'] for friend in user['friendslist']['friends']}.intersection(vertexes)])
        if len(_buffer) >= _buffer_max_size:
            g.add_edges(_buffer)
            _buffer=[]
        # g.add_edges([(user['steamid'],friend['steamid']) for friend in user['friendslist']['friends']])
    except Exception as e:
        print(e)
        pass

if len(_buffer) > 0:
    g.add_edges(_buffer)
    _buffer=[]
        
    # for friend in user['friendslist']['friends']:
            # pass
            # print(e)
            # print(friend)
            # print(user)
            # raise SystemError
            # pass

print("Graph created")

print(tabulate([[k,v] for k,v in graph.get_graph_infos(g).items()]))
print(g.summary())



fig = graph.plot_degree_distribution(g)
fig.savefig('degree_distribution.png')
fig = graph.plot_degree_distribution(g,type_='log')
fig.savefig('degree_distribution_log.png')
