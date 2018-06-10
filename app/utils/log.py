#! python3
"""
日志使用方法：
导入log.py
获取logger实例
from utils.log import logger
"""
from logging.handlers import TimedRotatingFileHandler
import logging
import sys, os

# 获取logger实例
logger = logging.getLogger(__name__)

# 指定输出的最低级别日志，默认WARN级别
logger.setLevel(logging.DEBUG)

# 设置日志输出格式
formatter = logging.Formatter('%(asctime)s\t%(threadName)s\t%(process)d\t%(thread)d\t%(filename)s\t%(' \
                              'funcName)s[line:%(lineno)d]\t%(levelname)s : %(message)s')

# 日志输出console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

# 获取路径
dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/log'
os.makedirs(dir_path, exist_ok=True)
log_path = dir_path + '/app.log'

# 日志输出到文件，文件按大小切分
file_handler = TimedRotatingFileHandler(log_path, when='D')
file_handler.setFormatter(formatter)

# 添加日志处理器
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def debug(msg):
    logging.debug(msg)
    logger.debug(msg)


def info(msg):
    logging.info(msg)
    logger.info(msg)


def warning(msg):
    logging.warning(msg)
    logger.warning(msg)


def error(msg):
    logging.error(msg)
    logger.error(msg)


def exception(msg):
    logging.exception(msg)
    logger.exception(msg)


if __name__ == '__main__':
    logger.info('hello')

"""
日志
logging.basicConfig函数各参数:
filename: 指定日志文件名
filemode: 和file函数意义相同，指定日志文件的打开模式，'w'或'a'
format: 指定输出的格式和内容，format可以输出很多有用信息，如上例所示:
 %(levelno)s: 打印日志级别的数值
 %(levelname)s: 打印日志级别名称
 %(pathname)s: 打印当前执行程序的路径，其实就是sys.argv[0]
 %(filename)s: 打印当前执行程序名
 %(funcName)s: 打印日志的当前函数
 %(lineno)d: 打印日志的当前行号
 %(asctime)s: 打印日志的时间
 %(thread)d: 打印线程ID
 %(threadName)s: 打印线程名称
 %(process)d: 打印进程ID
 %(message)s: 打印日志信息
datefmt: 指定时间格式，同time.strftime()
level: 设置日志级别，默认为logging.WARNING
stream: 指定将日志的输出流，可以指定输出到sys.stderr,sys.stdout或者文件，默认输出到sys.stderr，当stream和filename同时指定时，stream被忽略
"""
