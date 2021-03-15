from steam import webapi
import tqdm
import time
from pymongo import MongoClient
import utils

max_num_iterations = 95000

api = utils.create_api()

db = utils.start_db()


if db.users.estimated_document_count()>0:
    evaluated_users = db.users.find({}, {'steamid':1, 'friendslist':1 ,'_id':0})
    evaluated_users_id = set([i['steamid'] for i in evaluated_users])
    print(len(evaluated_users_id))

    users_to_evaluate_id = set()
    evaluated_users.rewind()
    for i in tqdm.tqdm(evaluated_users):
        # users_to_evaluate_id.union([j['steamid'] for j in i['friendslist']['friends']])
        users_to_evaluate_id = users_to_evaluate_id | set([j['steamid'] for j in i['friendslist']['friends']])
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

# users_data = {}
while len(users_to_evaluate_id) > 0 and num_iterations < max_num_iterations:
    try:
        # user_to_evaluate_id = users_to_evaluate_id.pop(np.random.randint(0,len(users_to_evaluate_id)))
        user_to_evaluate_id = users_to_evaluate_id.pop(0)
        num_iterations += 1
        print(num_iterations,user_to_evaluate_id,len(users_to_evaluate_id),len(evaluated_users_id))
        response = api.call('ISteamUser.GetFriendList', relationship='friend',steamid=user_to_evaluate_id)

        user_data = {}
        user_data.update(response)
        user_data['steamid'] = user_to_evaluate_id
        db['users'].insert_one(user_data)
        # print(response)
        # start_users_ids.append(response['response']['steamid'])
        
        evaluated_users_id.add(user_to_evaluate_id)
        users_to_evaluate_id.extend(list(set([i['steamid'] for i in response['friendslist']['friends']])-evaluated_users_id))
    except Exception as e:
        print(e)


