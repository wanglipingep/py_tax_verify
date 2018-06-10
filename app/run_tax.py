# coding:utf-8
from flask import Flask, request
from utils.log import logger as logging
from utils.global_res import mongo_db
from tax_info import tax

# 创建wsgi应用
app = Flask(__name__)


# 查验增值税发票
@app.route('/tax/query_tax', methods=['GET', 'POST'])
def query_tax():
    if request.method == "GET":
        return tax.query_tax(request.args.to_dict())
    else:
        return tax.query_tax(request.form.to_dict())


# 打开发票截图
@app.route('/tax/query_png')
def query_png():
    return tax.query_png(request.args.to_dict())


# 最近查验记录
@app.route('/')
@app.route('/tax/query_list')
def query_list():
    return tax.query_list(request.args.to_dict())


def reset_request_queue():
    logging.info('reset api_taxzz_crawled_record [state=-1]')
    mongo_db['api_taxzz_crawled_record'].update_many({"state": 1}, {"$set": {"state": -1}})


def main():
    reset_request_queue()
    app.run(host='0.0.0.0', port=5004, threaded=True)


# 启动程序
if __name__ == '__main__':
    main()
