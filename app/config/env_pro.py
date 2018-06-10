# coding:utf-8
######################## 公共配置 ########################
SPILT = '========================================'
# 环境标识（dev|test|pro）
LOCAL_ENV = 'pro'
# 实例标识（ams01|ams02）
LOCAL_INSTANCE = 'ams01'
# 线程池最大值
THREAD_POOL_MAX = 3
# 待爬队列最大失败次数
REQUEST_QUEUE_FAIL_MAX = 3

######################## selenium 配置 ########################
# selenium grid 分布式实例地址
HUB_URL = 'http://spider-grid.lls.com:4440/wd/hub'

######################## VPS 配置 ########################
# VPS服务地址
VPS_URL = 'http://127.0.0.1:5001/vps'
# 缓存到redis的代理池key
VPS_KEY = 'vps'

######################## MONGO 配置 ########################
# MONGO数据库配置
MONGODB_HOST = 'spiderdb.lls.com'
MONGODB_PORT = 27017
MONGODB_USERNAME = "llsspider"
MONGODB_PASSWORD = "Lls16888llsspider!"
MONGODB_DATABASE = "crawler"

# MONGO数据库表名
DB_REQUEST_QUEUE = 'api_request_queue'
DB_ENTERPRISE_CREDIT = 'api_enterprise_credit'

######################## MQ 配置 ########################
MQ_HOST = 'beemq1.lls.com'
MQ_PORT = '5672'
MQ_USENAME = 'llsspider'
MQ_PW = 'llsspider'
MQ_HOST_CRAW = '/crawl'

######################## AMS 配置 ########################
# 是否启动AMS MQ监听
START_MQ_REQUEST_AMS = 1  # 0关闭，1开启监听
# 全国工商信用信息的队列配置
MQ_REQUEST_NECIPS = 'dev.ams.crawl.ICustCrawlStartQueue'
MQ_RESPONSE_NECIPS = 'dev.ams.crawl.INecipsQueue'
# 全国工商信用信息截图存储路径
NECIPS_PATH = '/opt/spider_data/ams/'
TAX_PATH = '/opt/spider_data/ams/tax'

######################## REDIS 配置 ########################
REDIS_HOST = 'spredis.lls.com'
REDIS_PORT = 26379

######################## 响应码 配置 ########################
RESP_FAIL = {'resp_code': -1, 'reason': '请求失败'}
RESP_SUCCESS = {'resp_code': 0, 'reason': '请求成功'}
RESP_PARAM_ERROR = {'resp_code': 103, 'reason': '无效参数'}
RESP_CRAWLER_FAIL = {'resp_code': 101, 'reason': '爬取失败'}
RESP_CRAWLER_NODATA = {'resp_code': 102, 'reason': '爬取完成，数据不存在'}
RESP_CRAWLER_UNFINISHED = {'resp_code': 104, 'reason': '爬取未完成'}
RESP_CRAWLER_SUBMIT = {'resp_code': 200, 'reason': '请求成功，提交爬虫运行，爬取结果通过MQ返回'}

######################## 其他配置 ########################
