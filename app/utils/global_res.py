# coding:utf-8
import pymongo
from concurrent.futures import ThreadPoolExecutor
from config import env

# 初始化数据库连接
mongo_client = pymongo.MongoClient(env.MONGODB_HOST, env.MONGODB_PORT)
mongo_db = mongo_client[env.MONGODB_DATABASE]
mongo_db.authenticate(env.MONGODB_USERNAME, env.MONGODB_PASSWORD)

# 初始化线程池
thread_pool = ThreadPoolExecutor(env.THREAD_POOL_MAX)

# 服务器ip
# server_ip = socket.gethostbyname(socket.gethostname())

if __name__ == '__main__':
    row = mongo_db['api_resp_history'].find_one({}, sort=[['date', -1]])
    print(row.get('date'))

    # print(mongo_db['api_request_queue'].insert({"request_url": 3})) #1条
    # print(mongo_db['api_request_queue'].find_one_and_update({"request_url": 1}, {"$inc": {"request_url": 1}}))
    # print(mongo_db['api_request_queue'].find_one_and_update({}, {"$inc": {"request_url": 1}}).get('request_url')) #返回老数据
    # print(mongo_db['api_request_queue'].find_and_modify({},{"$inc": {"request_url": 1}})) #1条
    # print(mongo_db['api_request_queue'].update({}, {"$inc": {"request_url": 1}})) #1条
    # print(mongo_db['api_request_queue'].update_many({},{"$inc": {"request_url": 1}})) #多条
    # print(mongo_db['api_request_queue'].find_oneand_delete({}))

    # def say(i):
    #     for i in range(3):
    #         print('hello', i)
    #         time.sleep(1)
    # thread_pool.map(say, (1, 2))
