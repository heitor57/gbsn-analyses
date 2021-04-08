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
# parser.add_argument('--apps',
                    # type=str,
                    # default=['The Elder Scrolls III: Morrowind'],
                    # nargs='*')
# parser.add_argument('--max_num_iterations',
                    # type=int,
                    # help='Maximum number of iterations to do at crawling',
                    # default=30000)
args = parser.parse_args()

api = utils.create_api()

db = utils.start_db()

apps_ids = [i['appid'] for i in db.apps.find({'tags':{'$exists':False}})]

def get_app_tags(driver,app_id):

    url  = f"https://store.steampowered.com/app/{app_id}/"
    # response = requests.get(url)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tags = []
    tp = soup.find(class_='glance_tags_ctn popular_tags_ctn')
    data = dict()
    data['tags'] = None
    if tp != None:
        for a in tp.find_all('a'):
            # print(a['href'])
            tags.append(a.text.lstrip().rstrip())
        print(tags)
        data['tags'] = tags

    return data
    # time.sleep(6)

    # driver.find_element_by_css_selector('.glance_tags.popular_tags a')
    # selector = parsel.Selector(text=driver.page_source)
    # print(selector.css('.glance_tags').get())
options = FirefoxOptions()
options.add_argument("--headless")

try:
    driver = webdriver.Firefox(options=options)
    for app_id in tqdm(apps_ids):
        # if int(app_id) == 570:
        data = get_app_tags(driver,app_id)
        # print("EWQEWq")
        db.apps.update_one({'appid':app_id},{"$set": data})
        # print("EWQEWq")
            # break
    driver.close()

except:
    traceback.print_exc()
    driver.close()
  # print "Ate logo!" 
# appsid 




# = 
# for app in apps:

