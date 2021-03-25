
import utils
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--game',
                    type=str,
                    default='The Elder Scrolls III: Morrowind')
parser.add_argument('--max_num_iterations',type=int,help='Maximum number of iterations to do at crawling',default=30000)
args = parser.parse_args()

api = utils.create_api()
db = utils.start_db()

# appsids = db.apps.find({'reviews':{"$exists":False}}, {'appid':1, '_id':0})
app = db.apps.find_one({'name': args.game})


# evaluated_users = db.users.find({}, {
    # 'steamid': 1,
    # '_id': 0
# }).batch_size(args.batch_size)
# evaluated_users_id = {i['steamid'] for i in evaluated_users}

reviews = db.reviews.find({'appid':app['appid']})


evaluated_users = db.users.find({}, {
    'steamid': 1,
    '_id': 0
})
users_left = evaluated_users.count()
num_iterations = 0
evaluated_users_id = {i['steamid'] for i in evaluated_users}
for review in reviews:
    if review['author']['steamid'] not in evaluated_users_id:
        print(users_left,num_iterations,review['author']['steamid'])
        user_data=utils.get_user_data(api,review['author']['steamid'])
        db['users'].insert_one(user_data)
        evaluated_users_id |= {review['author']['steamid']}
        num_iterations +=1
    users_left -= 1
    if num_iterations >= args.max_num_iterations:
        break
