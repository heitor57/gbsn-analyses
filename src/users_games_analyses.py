import numpy as np
import time
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

appsid = [i['appid'] for i in db.apps.find({'name': {'$in': args.apps}})]


uids = {
    review['author']['steamid']
    for review in db.reviews.find({'appid': {'$in': appsid}}, {'author': 1})
}
uids= list(uids)

for user in db.users.find({'games':{'$exists':True},'steamid':{'$in':uids}},{'_id':0,'games':1,'game_count':1}):
    # print(type(user_games))
    # print(user_games.keys())
    print(user['game_count'])
    time.sleep(1)
