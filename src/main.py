from steam import webapi
import pymongo
import numpy as np
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
import tqdm
import time
from pymongo import MongoClient
import utils

num_processes = 1
num_max_tasks = 1
max_num_iterations = 30000
batch_size = 10000
construction_buffer_max_size = 10000

api = utils.create_api()

db = utils.start_db()

if db.users.estimated_document_count() > 0:
    evaluated_users = db.users.find({}, {
        'steamid': 1,
        '_id': 0
    }).batch_size(batch_size)
    evaluated_users_id = {i['steamid'] for i in evaluated_users}
    # assert("76561198155702016" in evaluated_users_id)
    print('Number of evaluated users',len(evaluated_users_id))

    users_to_evaluate_id_set = set()
    evaluated_users = db.users.find({
        "friendslist": {
            "$exists": True
        }
    }, {
        'steamid': 1,
        'friendslist': 1,
        '_id': 0
    }).batch_size(batch_size)
    users_to_evaluate_id_buffer = list()
    for i in tqdm.tqdm(evaluated_users):
        users_to_evaluate_id_buffer.extend(
            [j['steamid'] for j in i['friendslist']['friends']])
        if len(users_to_evaluate_id_buffer) >= construction_buffer_max_size:
            users_to_evaluate_id_set |= set(users_to_evaluate_id_buffer)
            users_to_evaluate_id_buffer = []
    if len(users_to_evaluate_id_buffer) > 0:
        users_to_evaluate_id_set |= set(users_to_evaluate_id_buffer)
        users_to_evaluate_id_buffer = []

    # print(len(users_to_evaluate_id))
    users_to_evaluate_id_set = users_to_evaluate_id_set - set(evaluated_users_id)
    users_to_evaluate_id_list = list(users_to_evaluate_id_set)
    # users_to_evaluate_id_set = set(users_to_evaluate_id)

    del evaluated_users
else:
    raise SystemError
    users_to_evaluate_id = ['heitorhlw']
    start_users_ids = []
    for user in users_to_evaluate_id:
        v = api.call('ISteamUser.ResolveVanityURL', vanityurl=user, url_type=1)
        start_users_ids.append(v['response']['steamid'])
    users_to_evaluate_id = start_users_ids
    evaluated_users_id = set()

def get_user_data(user_id):
    try:
        response = api.call('ISteamUser.GetFriendList',
                            relationship='friend',
                            steamid=user_id)
        user_data = {}
        user_data.update(response)
        user_data['steamid'] = user_to_evaluate_id
        return user_data
    except Exception as e:
        print(e)
        return {'steamid': user_id, 'invalid': True}

num_iterations = 0

while len(users_to_evaluate_id_set) > 0 and num_iterations < max_num_iterations:
    user_to_evaluate_id = users_to_evaluate_id_list.pop(
        np.random.randint(0, len(users_to_evaluate_id_list)))
    users_to_evaluate_id_set -= set([user_to_evaluate_id])
    num_iterations += 1
    user_data = get_user_data(user_to_evaluate_id)
    db['users'].insert_one(user_data)
    evaluated_users_id.add(user_data['steamid'])
    if "friendslist" in user_data:
        friends = set([
            friend['steamid']
            for friend in user_data['friendslist']['friends']
        ])
        friends -= evaluated_users_id
        friends -= users_to_evaluate_id_set
        users_to_evaluate_id_list.extend(list(friends))
        users_to_evaluate_id_set |= friends
        # users_to_evaluate_id_set |= friends
