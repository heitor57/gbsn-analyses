import numpy as np
import time
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver

import requests
import argparse
import utils
from scipy import *
import parsel
import igraph
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

apps = db.apps.find()

def get_app_tags(driver,app_id):

    url  = f"https://store.steampowered.com/app/{app_id}/"
    # response = requests.get(url)
    driver.get(url)

    time.sleep(6)

    print(driver.find_element_by_css_selector('.glance_tags'))
    # selector = parsel.Selector(text=driver.page_source)
    # print(selector.css('.glance_tags').get())
options = FirefoxOptions()
options.add_argument("--headless")

try:
    driver = webdriver.Firefox('.',options=options)
    for app in apps:
        get_app_tags(driver,app['appid'])
        break

    driver.close()

except:
  driver.close()
  # print "Ate logo!" 
# appsid 




# = 
# for app in apps:

