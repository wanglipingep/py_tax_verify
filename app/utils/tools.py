# coding:utf-8
import json
import uuid
import time
from config import env
from utils.log import logger as logging
from utils.global_res import mongo_db
import urllib
import os
import requests


# 把class对象转换成dict类型的对象
def convert_to_builtin_type(obj):
    d = {}
    d.update(obj.__dict__)
    return d


# 把class对象或python对象转换成json
def toJson(obj):
    # return json.dumps(obj, default=convert_to_builtin_type)
    return json.dumps(obj, default=convert_to_builtin_type, ensure_ascii=False)  # 显示中文


# 把class对象转换成dict对象
def toDict(obj):
    return json.loads(toJson(obj))


# 把json字符串转换成dict对象
def json2Dict(str):
    return json.loads(str)


# 转换中文key，注意中英名称顺序一致
# 例如man={'姓名':1,'年龄',2}->{'name':1,'age':2}
# chineseNames=['姓名','年龄']
# englishNames=['name','age']
# 调用convertName(man, chineseNames, englishNames)
def convertName(obj, chineseNames, englishNames):
    newobj = {}
    for i in range(len(chineseNames)):
        if chineseNames[i] in obj:
            newobj.setdefault(englishNames[i], obj.get(chineseNames[i]))
    return newobj


# 返回01559a0a804aa611e8a04f54e1adcf8e4b
def getUuid():
    return str(uuid.uuid1()).replace("-", "").lower()


# 传入调用程序的__file__, 返回调用程序的当前目录下的子目录路径，没有会创建
def getSubdir(fpath, subdir):
    subdir_path = os.path.dirname(os.path.abspath(fpath)) + os.sep + subdir
    os.makedirs(subdir_path, exist_ok=True)
    return subdir_path + os.sep


# 获取截屏的临时文件名称
def getScreenshotName(fpath):
    subdir_path = getSubdir(fpath, 'captcha')
    os.makedirs(subdir_path, exist_ok=True)
    return subdir_path + 'screenshot_' + getUuid() + '.png'


# 获取验证码截图的临时文件名称
def getCaptchaName(fpath):
    subdir_path = getSubdir(fpath, 'captcha')
    os.makedirs(subdir_path, exist_ok=True)
    return subdir_path + 'captcha_' + getUuid() + '.png'


# 返回标准响应，resp为统一定义的响应码，可扩展返回参数
def getJsonResp(resp, **kwargs):
    kwargs.update(resp)
    return toJson(kwargs)


# 设置参数，如参数为空则不设置，可对参数值进行安全校验
def get_params(keys, source):
    result = {}
    for key in keys:
        if source.get(key):
            result[key] = source[key]
    return result


# 检查非空参数
def check_params(keys, source):
    for key in keys:
        if not source.get(key):
            return False
    return True


# url解码
def decodeUrl(url):
    return urllib.parse.unquote(url)


# 返回创建时间（豪秒）
def getTime():
    return int(round(time.time() * 1000))


# 返回创建时间（日期字符串）
def getFormatTime():
    return time.strftime('%Y-%m-%d %H:%M:%S')


# 从秒转换为时间字符串
def getFormatTimeFrom(seconds):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds))


# 插入待爬队列
def insert_request_queue(**kwargs):
    try:
        kwargs['exe_state'] = 1  # 执行状态 0:休眠,1:执行
        kwargs['exe_num'] = 1  # 执行次数
        kwargs['create_time'] = getTime()
        mongo_db['api_request_queue'].insert(kwargs)
        logging.info('insert_request_queue data=%s' % kwargs)
    except Exception as err:
        raise Exception('insert_request_queue fail data=%s err=%s' % (kwargs, err))


# 按指定条件清除失败记录
def removeRequestQueue(query_con, reason):
    request_url = query_con.get('request_url')
    if mongo_db['api_request_queue'].find_one_and_delete(query_con):
        logging.info("remove url=%s from api_request_queue" % request_url)
        insertRequestHistory(request_url=request_url, reason=reason)


# 更新待爬队列的执行状态 0:休眠,1:执行
# 休眠状态会通过轮询线程唤醒
# 失败记录通过指定条件清除
def updateRequestQueueState(url, state):
    logging.info("update api_request_queue url=%s state to %s" % (url, state))
    if state == 1:
        # 锁定执行
        mongo_db['api_request_queue'].find_one_and_update({'request_url': url},
                                                          {"$set": {"exe_state": state},
                                                           "$inc": {"exe_num": 1}})
    if state == 0:
        # 执行失败
        mongo_db['api_request_queue'].find_one_and_update({'request_url': url},
                                                          {"$set": {"exe_state": state}})
        # 删除多次失败的记录，避免阻塞新的请求插入
        query_con = {'request_url': url, "exe_state": 0, "exe_num": {'$gt': env.REQUEST_QUEUE_FAIL_MAX}}
        removeRequestQueue(query_con, 'fail')


# 重启服务时重置待爬队列的执行状态（关闭服务时线程池的任务都lock了需要释放）
def resetRequestQueue():
    mongo_db['api_request_queue'].update_many({}, {"$set": {"exe_state": 0, "exe_num": 0}})
    logging.info("reset api_request_queue")


# 检查待爬队列的执行状态
def checkRequestQueue():
    running_count = mongo_db['api_request_queue'].find({"exe_state": 1}).count()
    sleeping_count = mongo_db['api_request_queue'].find({"exe_state": 0}).count()
    logging.info('listennerThread api_request_queue running=%d, sleeping=%d' % (running_count, sleeping_count))


# 保存请求记录，包含成功、异常、失败记录
def insertRequestHistory(**kwargs):
    kwargs['create_time'] = getTime()
    mongo_db['api_request_history'].insert(kwargs)


# 保存请求异常
def insertRequestError(request_url, err):
    insertRequestHistory(request_url=request_url, reason=err)


# 保存拨号异常
def insert_dialup_err(**kwargs):
    kwargs['create_time'] = getTime()
    mongo_db['vps_dialup_error'].insert(kwargs)


# 插入记录，并发情况下需要通过唯一索引保证唯一记录
def insert_one(table, data):
    try:
        data['create_time'] = getTime()
        # data['update_time'] = now
        # data['state'] = 0  # 执行状态 [0:空闲,1:执行中,2:执行成功,-1:执行失败]
        mongo_db[table].insert(data)
    except Exception as err:
        logging.exception(err)


def update_one(table, query_args, update_args):
    return mongo_db[table].find_one_and_update(query_args, update_args, sort=[['create_time', -1]])


def delete_one(table, query_args):
    return mongo_db[table].find_one_and_delete(query_args, sort=[['create_time', -1]])


def query_one(table, query_args):
    return mongo_db[table].find_one(query_args, {'_id': 0}, sort=[['create_time', -1]])


def query_list(table, query_args):
    return mongo_db[table].find(query_args, {'_id': 0}, sort=[['create_time', -1]]).limit(50)


def query_list_with_keys(table, query_args, sort=True):
    if sort:
        rows = list(mongo_db[table].find(query_args, {'_id': 0}, sort=[['create_time', -1]]).limit(50))
    else:
        # 大数据量查询时不排序
        rows = list(mongo_db[table].find(query_args, {'_id': 0}).limit(50))

    for row in rows:
        row['create_time'] = getFormatTimeFrom(row['create_time'] / 1000)
    keys = []
    if rows:
        keys = list(rows[0].keys())
    return rows, keys


def query_count(table, query_args):
    return mongo_db[table].find(query_args).count()

# 代理有效性检测
def is_ip_ok(vps):
    ip = vps.split('|')[1]
    proxies = {
        "http": ip
    }
    for i in range(2):
        try:
            # v_sunnet_b回拨的ip可即用，v_sunnet_a需二次请求才能用，延时并不起作用
            resp = requests.get('http://www.baidu.com', proxies=proxies, timeout=6)
            logging.info('vps=%s test status_code=%s' % (vps, resp.status_code))
            if resp.status_code == 200:
                return True
        except Exception as err:
            logging.warning('vps=%s test fail=%s' % (vps, err))
    return False


if __name__ == '__main__':
    print(getFormatTimeFrom(1526384839))
