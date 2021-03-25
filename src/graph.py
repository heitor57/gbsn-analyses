
import numpy as np
import igraph
import scipy.optimize
import matplotlib.pyplot as plt


def get_graph_infos(g):
    infos = {}
    infos['Number of vertices'] = g.vcount()
    infos['Number of edges'] = g.ecount()
    infos['Mean Degree'] = np.mean(g.degree())
    infos['Min Degree'] = np.min(g.degree())
    infos['Max Degree'] = np.max(g.degree())
    infos['Density'] = g.density(loops=False)
    infos['Sparsity'] = 1-g.density(loops=False)
    # infos['c'] = transitivity_undirected
    # infos['density 2'] = 2*g.ecount()/((g.vcount()-1)*g.vcount())
    infos['Clustering coefficient'] = g.transitivity_avglocal_undirected(mode="zero")
    infos['Radius'] = g.radius()
    infos['Diameter'] = g.diameter()
    infos['Girth'] = g.girth()
    return infos
def plot_degree_distribution(g,type_=None):
    fit_function = lambda k, a: k**a
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
