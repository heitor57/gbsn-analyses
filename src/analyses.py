import numpy as np
import utils
from scipy import *
import igraph
from tqdm import tqdm
from tabulate import tabulate
import matplotlib.pyplot as plt
import scipy.optimize
from sympy import *

# k,a = symbols('k a')
# fit_function = k**a
# lambda_fit_function = lambdify([k,a],fit_function)
fit_function = lambda k,a: k**a

db = utils.start_db()

g = igraph.Graph(directed=False)

vertexes = set()
for user in tqdm(db.users.find({"friendslist": {
            "$exists": True
            }},{'_id':0,'steamid':1}).batch_size(10000).limit(20000)):
    g.add_vertices(user['steamid'])
    vertexes.add(user['steamid'])
 

for user in tqdm(db.users.find({"friendslist": {
            "$exists": True
            }},{'_id':0,'steamid':1,'friendslist':1}).batch_size(10000).limit(20000)):
    # print(user['friendslist']['friends'])
    try:
        g.add_edges([(user['steamid'],i) for i in {friend['steamid'] for friend in user['friendslist']['friends']}.intersection(vertexes)])
        # g.add_edges([(user['steamid'],friend['steamid']) for friend in user['friendslist']['friends']])
    except Exception as e:
        print(e)
        pass
        
    # for friend in user['friendslist']['friends']:
            # pass
            # print(e)
            # print(friend)
            # print(user)
            # raise SystemError
            # pass

print("Graph created")

def get_graph_infos(g):
    infos = {}
    infos['Number of vertices'] = g.vcount()
    infos['Number of edges'] = g.ecount()
    infos['Mean Degree'] = np.mean(g.degree())
    infos['Density'] = g.density(loops=False)
    infos['Sparsity'] = 1-g.density(loops=False)
    # infos['c'] = transitivity_undirected
    # infos['density 2'] = 2*g.ecount()/((g.vcount()-1)*g.vcount())
    infos['Clustering coefficient'] = g.transitivity_avglocal_undirected(mode="zero")
    infos['Radius'] = g.radius()
    infos['Diameter'] = g.diameter()
    infos['Girth'] = g.girth()
    return infos

print(tabulate([[k,v] for k,v in get_graph_infos(g).items()]))
print(g.summary())


def plot_degree_distribution(g,type_=None):
    fig, ax = plt.subplots()
    # max_degree = max(g.degree())
    values, counts = np.unique(g.degree(), return_counts=True)
    counts = counts/np.sum(counts)
    if type_=='log':
        ax.set_xscale('log')
        ax.set_yscale('log')



    ax.scatter(x=values,y=counts,facecolors='none',edgecolors='k')
    ax.set_xlabel('Degree')
    ax.set_ylabel('Probability(Degree)')

    popt, pcov= scipy.optimize.curve_fit(fit_function,xdata=values,ydata=counts)
    # fitted_function = fit_function.subs(a, UnevaluatedExpr(popt[0]))
    # fitted_function = lambdify(k,fitted_function)
    # fitted_function = lambda k: k**popt[0]

    line = ax.plot(values,list(map(lambda k: fit_function(k,popt[0]),values)),color='k')

    s= f'Fitted line ($k^{{{popt[0]:.2f}}}$)'
    print(s)
    ax.legend([s,'Collected data'])
    # print(lambda_fit_function(1,2))

    # ax.set_title(latex(fitted_function))
    
    return fig

fig = plot_degree_distribution(g)
fig.savefig('degree_distribution.png')
fig = plot_degree_distribution(g,type_='log')
fig.savefig('degree_distribution_log.png')
