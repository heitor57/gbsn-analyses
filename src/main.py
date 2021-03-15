from steam import webapi
import pymongo
import numpy as np
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
import tqdm
import time
from pymongo import MongoClient
import utils

num_ptasks = 4
max_num_iterations = 30000
batch_size = 10000
construction_buffer_max_size = 10000

api = utils.create_api()

db = utils.start_db()

if db.users.estimated_document_count()>0:
    evaluated_users = db.users.find({}, {'steamid':1, 'friendslist':1 ,'_id':0}).batch_size(batch_size)
    evaluated_users_id = {i['steamid'] for i in evaluated_users}
    print(len(evaluated_users_id))

    users_to_evaluate_id = set()
    evaluated_users = db.users.find({"invalid" : { "$exists" : False }}, {'steamid':1, 'friendslist':1 ,'_id':0}).batch_size(batch_size)
    users_to_evaluate_id_buffer = list()
    for i in tqdm.tqdm(evaluated_users):
        users_to_evaluate_id_buffer.extend([j['steamid'] for j in i['friendslist']['friends']])
        if len(users_to_evaluate_id_buffer) >= construction_buffer_max_size:
            users_to_evaluate_id |= set(users_to_evaluate_id_buffer)
            users_to_evaluate_id_buffer = []
    if len(users_to_evaluate_id_buffer)>0:
        users_to_evaluate_id |= set(users_to_evaluate_id_buffer)
        users_to_evaluate_id_buffer = []

    print(len(users_to_evaluate_id))
    users_to_evaluate_id = list(users_to_evaluate_id - evaluated_users_id)

    del evaluated_users
else:
    users_to_evaluate_id = ['heitorhlw']
    start_users_ids = []
    for user in users_to_evaluate_id:
        v = api.call('ISteamUser.ResolveVanityURL', vanityurl=user, url_type=1)
        start_users_ids.append(v['response']['steamid'])
    users_to_evaluate_id=start_users_ids
    evaluated_users_id = set()

num_iterations = 0

def get_user_data(user_id):
    response = api.call('ISteamUser.GetFriendList', relationship='friend',steamid=user_id)
    user_data = {}
    user_data.update(response)
    user_data['steamid'] = user_to_evaluate_id
    return user_data

    # print(response)
    # start_users_ids.append(response['response']['steamid'])

    # users_to_evaluate_id.extend(list(set([i['steamid'] for i in user_data['friendslist']['friends']])-evaluated_users_id))


# with ProcessPoolExecutor(num_ptasks) as executor:

    # futures = set()
    # while len(users_to_evaluate_id) > 0 and num_iterations < max_num_iterations:
        # user_to_evaluate_id = users_to_evaluate_id.pop(np.random.randint(0,len(users_to_evaluate_id)))
        # num_iterations += 1
        # evaluated_users_id.add(user_to_evaluate_id)
        # f = executor.submit(get_user_data,user_to_evaluate_id)
        # futures.add(f)
        # if len(futures) >= num_ptasks:
            # completed, futures = wait(futures, return_when=FIRST_COMPLETED)

    # for f in futures:
        # f.result()


while len(users_to_evaluate_id) > 0 and num_iterations < max_num_iterations:
    try:
        try:
            user_to_evaluate_id = users_to_evaluate_id.pop(np.random.randint(0,len(users_to_evaluate_id)))
            # user_to_evaluate_id = users_to_evaluate_id.pop(0)
            num_iterations += 1
            evaluated_users_id.add(user_to_evaluate_id)
            print(num_iterations,user_to_evaluate_id,len(users_to_evaluate_id),len(evaluated_users_id))

            response = api.call('ISteamUser.GetFriendList', relationship='friend',steamid=user_to_evaluate_id)

            user_data = {}
            user_data.update(response)
            user_data['steamid'] = user_to_evaluate_id
            db['users'].insert_one(user_data)
            # print(response)
            # start_users_ids.append(response['response']['steamid'])
            
            users_to_evaluate_id.extend(list(set([i['steamid'] for i in response['friendslist']['friends']])-evaluated_users_id))
        except Exception as e:
            print(e)
            db['users'].insert_one({'steamid': user_to_evaluate_id,'invalid':True})
    except pymongo.errors.DuplicateKeyError as e:
        print(e)
