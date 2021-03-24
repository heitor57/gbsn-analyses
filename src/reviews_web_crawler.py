from pymongo import MongoClient
import pymongo
import urllib
import traceback
import os
import requests
import time
import concurrent.futures
import parsel
from steam import webapi
import utils
import argparse
import yaml

def form_extract_data(form):
    action = form.xpath('@action').extract_first()
    names = form.xpath('input/@name').extract()
    values = form.xpath('input/@value').extract()
    return action,dict(zip(names, values))
def get_data_from_review(review):
    data = dict()
    data['steamid'] = review.css(
        '.apphub_CardContentAuthorName a::attr(href)').re_first('.*/profiles/(.+)/')
    if data['steamid'] == None:
        user = review.css(
            '.apphub_CardContentAuthorName a::attr(href)').re_first('.*/id/(.+)/')

        api = utils.create_api()
        v = api.call('ISteamUser.ResolveVanityURL', vanityurl=user, url_type=1)
        data['steamid']=v['response']['steamid']
    data['recommended'] = review.css('.title::text').get()
    data['user_name'] = review.css(
        '.apphub_CardContentAuthorName a::text').get()
    data['date'] = review.css('.date_posted::text').re_first('Posted: (.+)')
    data['text'] = review.css('.apphub_CardTextContent::text').getall()

    data['hours'] = review.css('.hours::text').re_first('(.+) hrs')
    data['compensation'] = review.css('.received_compensation::text').get()

    data['products'] = review.css('.apphub_CardContentMoreLink ::text').re_first('([\d,]+) product')

    feedback = review.css('.found_helpful ::text')
    data['found_helpful'] = feedback.re_first('([\d,]+).*helpful')
    data['found_funny'] = feedback.re_first('([\d,]+).*funny')
    early_access = review.css('.early_access_review').get()
    if early_access:
        data['early_access']= True
    else:
        data['early_access']= False
    return data

def scrapy_page(html):
    selector = parsel.Selector(html)
    reviews = selector.css('div .apphub_Card')
    reviews_data = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.max_workers) as executor:
        for review in reviews:
            # print(review.get())
            review_data=  get_data_from_review(review)
            # print(yaml.dump(review_data))
            reviews_data.append(review_data)
    return reviews_data

parser = argparse.ArgumentParser()
parser.add_argument('--app',
                    type=str,
                    default='The Elder Scrolls III: Morrowind')
parser.add_argument('--max_workers',
                    default=os.cpu_count())
args = parser.parse_args()
args.max_workers =  int(args.max_workers)

db = utils.start_db()

app = db.apps.find_one({'name': args.app})

appid = app['appid']

seed = f"https://steamcommunity.com/app/{appid}/reviews/?filterLanguage=all&p=1&browsefilter=toprated"
print(seed)
response = requests.get(seed)

# while response:
num_pages = 0
while True:

    reviews_data = scrapy_page(response.text)
    print(len(reviews_data),"!!!!!!")
    num_pages +=1
    print('Num pages crawled',num_pages)
    selector = parsel.Selector(response.text)
    form = selector.xpath('//form[contains(@id, "MoreContentForm")]')
    # print(form.get())

    if form.get():
        action,dict_form = form_extract_data(form)
        response = requests.get(action,params=dict_form)
        # open('outteste.html','w+').write(response.text)
    else:
        break


# print(app['name'],appid)
# cursor = '*'
# is_end = False
# num_per_page = 100
# while not is_end:
# print(cursor)
# try:
# s = f'https://store.steampowered.com/appreviews/{appid}?json=1&cursor={cursor}&filter=recent&num_per_page={num_per_page}'
# print(s)
# response = requests.get(url=s)
# response = response.json()
# if cursor == urllib.parse.quote(response["cursor"]):
# raise SystemError("Loop")
# cursor = urllib.parse.quote(response["cursor"])
# is_end = not (response['query_summary']['num_reviews'] == num_per_page)
# # print(response)
# for review in response['reviews']:
# review['appid'] = appid
# db.reviews.insert_many(response['reviews'],ordered=False)
# except pymongo.errors.BulkWriteError as e:
# print("Bulk write error")
