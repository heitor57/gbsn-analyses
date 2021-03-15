from steam import webapi
import time
from pymongo import MongoClient
import utils



api = utils.create_api()

db = utils.start_db()

buffer_size = 100
steamids = db.users.find({'profileurl':{"$exists":False}}, {'steamid':1, '_id':0})

# print(len(list(steamids)))

# raise SystemError
ids_buffer = []
for steamid in steamids:
    ids_buffer.append(steamid['steamid'])

    if len(ids_buffer) == buffer_size:
        print("call")
        response = api.call('ISteamUser.GetPlayerSummaries',steamids=','.join(ids_buffer))
        print(response)
        for player in response['response']['players']:
            try:
                steamid = player.pop('steamid')
            except Exception as e:
                print(e)
            db.users.update_one({"steamid":steamid},{"$set":player})
        ids_buffer = []

if len(ids_buffer) > 0:
    print("call")
    response = api.call('ISteamUser.GetPlayerSummaries',steamids=','.join(ids_buffer))
    for player in response['response']['players']:
        try:
            steamid = player.pop('steamid')
        except Exception as e:
            print(e)
        db.users.update_one({"steamid":steamid},{"$set":player})
        ids_buffer = []

# while len(users_to_evaluate) > 0 and num_iterations < max_num_iterations:
    # try:
        # user_to_evaluate = users_to_evaluate.pop(0)
        # num_iterations += 1
        # print(num_iterations,user_to_evaluate,len(users_to_evaluate))
        # response = api.call('ISteamUser.GetFriendList', relationship='friend',steamid=user_to_evaluate)

        # user_data = {}
        # user_data.update(response)
        # user_data['steamid'] = user_to_evaluate
        # db['users'].insert_one(user_data)
        # # print(response)
        # # start_users_ids.append(response['response']['steamid'])
        
        # evaluated_users.add(user_to_evaluate)
        # users_to_evaluate.extend(list(set([i['steamid'] for i in response['friendslist']['friends']])-evaluated_users))
    # except Exception as e:
        # print(e)


