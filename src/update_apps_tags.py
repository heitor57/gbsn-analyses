import numpy as np

import traceback
import time
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver

import requests
import argparse
import utils
from scipy import *
import parsel
import igraph
from bs4 import BeautifulSoup
from tqdm import tqdm
from tabulate import tabulate
import matplotlib.pyplot as plt
import scipy.optimize
from sympy import *
import graph
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys

import urllib.parse
parser = argparse.ArgumentParser()
parser.add_argument('--apps',
                    type=str,
                    default=['The Elder Scrolls III: Morrowind'],
                    nargs='*')
# parser.add_argument('--max_num_iterations',
                    # type=int,
                    # help='Maximum number of iterations to do at crawling',
                    # default=30000)
args = parser.parse_args()

api = utils.create_api()

db = utils.start_db()

appsid = [i['appid'] for i in db.apps.find({'name':{'$in':args.apps}})]

uids = {
    review['author']['steamid']
    for review in db.reviews.find({'appid': {
        '$in': appsid
        }}, {'author': 1})
}
uids = list(uids)
games = set()
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
                'games': 1,
            }).batch_size(10000)):
    # print(user)
    if user['games'] != None:
        games |= set([g['appid'] for g in user['games']])

apps_ids_updated ={i['appid'] for i in db.apps.find({'price':{'$exists':True}})}
games = games - apps_ids_updated

def get_app_tags(driver,app_id):

    url  = f"https://store.steampowered.com/app/{app_id}/"
    # response = requests.get(url)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tags = []
    tp = soup.find(class_='glance_tags_ctn popular_tags_ctn')
    data = dict()
    data['appid'] = app_id
    data['tags'] = None
    if tp != None:
        for a in tp.find_all('a'):
            # print(a['href'])
            tags.append(a.text.lstrip().rstrip())
        print(tags)
        data['tags'] = tags
    data['price']=None 
    tmp = soup.find(class_='game_purchase_price price')
    if tmp != None:
        # print(tmp)
        if 'data-price-final' in tmp:
            data['price']=int(tmp['data-price-final'])
    data['release_date'] = None
    t1= soup.find(class_='release_date')
    if t1:
        data['release_date']=t1.find(class_='date').text.lstrip().rstrip()
    data['developers_list'] = []
    try:
        for dev in soup.find(id='developers_list').find_all('a'):
            data['developers_list'].append(dev.text.lstrip().rstrip())
    except:
        pass

    return data
    # time.sleep(6)

    # driver.find_element_by_css_selector('.glance_tags.popular_tags a')
    # selector = parsel.Selector(text=driver.page_source)
    # print(selector.css('.glance_tags').get())
options = FirefoxOptions()
options.add_argument("--headless")

apps_ids = list(games)
# print(len(apps_ids))
try:
    driver = webdriver.Firefox(options=options)
    for app_id in tqdm(apps_ids):
        data = get_app_tags(driver,app_id)
        print(app_id,data)
        # print()
        r= db.apps.update_one({'appid':app_id},{"$set": data},True)
        print(r.raw_result)
    driver.close()

except:
    traceback.print_exc()
    driver.close()
  # print "Ate logo!" 
# appsid 




# = 
# for app in apps:

