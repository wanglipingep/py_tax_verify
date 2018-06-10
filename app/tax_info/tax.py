# coding:utf-8
"""
  增值税查询接口
  https://inv-veri.chinatax.gov.cn/
"""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from PIL import Image
from config import env
from utils import tools
from utils.log import logger as logging
from utils.global_res import thread_pool
from utils.yzm91 import Recoginze
import time
from flask import render_template, make_response


class TaxVeri(object):
    def __init__(self, params):
        self.params = params
        self.fpdm = params['fpdm']
        self.fphm = params['fphm']
        self.kprq = params['kprq']
        self.kjje = params['kjje']
        self.png_name = ''
        self.gfmc_pp = ''

    def query(self):
        # driver = webdriver.Firefox()
        driver = WebDriver(
            command_executor=env.HUB_URL,
            desired_capabilities=DesiredCapabilities.FIREFOX.copy()
        )
        driver.maximize_window()  # 全屏避免低分辨率显示不全
        driver.implicitly_wait(10)
        try:
            begin_time = time.time()
            logging.info(env.SPILT)
            logging.info('query begin [fpdm=%s fphm=%s]' % (self.fpdm, self.fphm))
            driver.get('https://inv-veri.chinatax.gov.cn/')

            # 填充信息
            self.fill_field(driver)

            # 处理验证码
            if not self.decode_captcha(driver):
                return

            # 执行查询
            self.process_page(driver)

            cost_time = round(time.time() - begin_time)
            logging.info("query finished [png_name=%s, cost_time=%s]" % (self.png_name, cost_time))

            tools.update_one('api_taxzz_crawled_record', self.params,
                             {"$set": {"state": 2,
                                       'png_name': self.png_name,
                                       'gfmc_pp': self.gfmc_pp
                                       }})
            return self.png_name

        except Exception as err:
            logging.exception('query fail')
            tools.update_one('api_taxzz_crawled_record', self.params, {"$set": {"state": -1}})
            raise err
        finally:
            if driver:
                logging.info('close selenium driver')
                driver.quit()

    def fill_field(self, driver):
        # logging.info("process_list [pageNo=%s]" % self.pageNo)
        fpdm = driver.find_element_by_id("fpdm")
        fpdm.clear()
        fpdm.send_keys(self.fpdm)
        fphm = driver.find_element_by_id("fphm")
        fphm.clear()
        fphm.send_keys(self.fphm)
        kprq = driver.find_element_by_id("kprq")
        kprq.clear()
        kprq.send_keys(self.kprq)
        kjje = driver.find_element_by_id("kjje")
        kjje.clear()
        kjje.send_keys(self.kjje)
        time.sleep(1)  # 等待输入触发事件

        # 如果填充信息有误
        if 'tip_common_wrong' in driver.page_source:
            raise Exception('填写信息有误')
        # logging.info("process_list end")

    def process_page(self, driver):
        logging.info("process_page begin")

        # 提取消息
        self.gfmc_pp = driver.find_element_by_id('gfmc_pp').text

        # 保存截图
        body = driver.find_element_by_tag_name('body')
        scrollWidth = body.get_attribute('scrollWidth')
        scrollHeight = body.get_attribute('scrollHeight')
        driver.set_window_size(scrollWidth, scrollHeight)
        fname = '%s_%s.png' % (self.fpdm, self.fphm)
        fpath = env.TAX_PATH + fname
        if env.LOCAL_ENV == 'dev':
            fpath = tools.getSubdir(__file__, 'png') + fname
        driver.save_screenshot(fpath)
        self.png_name = fname
        logging.info("process_page save screenshot")
        # logging.info("process_page end")

    # 处理验证码
    def decode_captcha(self, driver):
        logging.info("decode_captcha begin")
        tmp_driver = None
        for i in range(5):
            try:
                # 如果已通过验证
                if '查验时间' in driver.page_source:
                    logging.info('decode_captcha success with tax content')
                    return True

                # 截取验证码图片，这里先提取验证码和文字提示，通过新窗口打开并截屏
                def wait1(driver):
                    return '请输入验证码图片' in driver.page_source or '请输入验证码文字' in driver.page_source

                try:
                    WebDriverWait(driver, 10).until(wait1, 'decode_captcha fail to find yzm')
                except:
                    # 如果不显示验证码，刷新页面
                    driver.refresh()
                    self.fill_field(driver)
                    continue

                yzminfo_html = driver.find_element_by_id("yzminfo").get_attribute('outerHTML')
                captcha_html = driver.find_element_by_id("yzm_img").get_attribute('outerHTML')
                # 提取出来的display设置了none，这里修改下
                # print(yzminfo_html, captcha_html)
                captcha_html = captcha_html.replace('display: none;', 'display: inline;')

                # tmp_driver = webdriver.Firefox()
                tmp_driver = WebDriver(
                    command_executor=env.HUB_URL,
                    desired_capabilities=DesiredCapabilities.FIREFOX.copy()
                )
                # 使用一个空白html打开，图像src是base64数据打开无法截屏
                # tmp_driver.get(captcha_image.get_attribute('src'))
                tmp_driver.get('http://www.baidu.com')
                # 将提取的验证码和提示拼接到html
                tmp_driver.execute_script("""
                    document.body.innerHTML = arguments[0]
                """, yzminfo_html + '<br>' + captcha_html)

                screenshotName = tools.getScreenshotName(__file__)
                tmp_driver.save_screenshot(screenshotName)
                logging.info('decode_captcha save_screenshot')

                captcha_image = tmp_driver.find_element_by_tag_name("img")
                location = captcha_image.location
                size = captcha_image.size
                left = location['x']
                top = location['y']
                right = left + size['width'] + 120
                bottom = top + size['height'] + 20
                im = Image.open(screenshotName)
                im = im.crop((0, 0, right, bottom))
                captchaName = tools.getCaptchaName(__file__)
                im.save(captchaName)

                start_time = time.time()
                errcode, result = Recoginze(captchaName, 8023)
                if result[0] == "#":
                    # 解码超时或出错时刷新验证码
                    driver.find_element_by_id("yzm_img").click()
                    time.sleep(3)
                    raise Exception("91打码解析验证码失败 [errcode=%s, result=%s]" % (errcode, result))
                cost_time = round(time.time() - start_time)
                logging.info('decode_captcha [result=%s, costtime=%s]' % (result, cost_time))

                yzm = driver.find_element_by_id("yzm")
                yzm.clear()
                yzm.send_keys(result)
                time.sleep(1)

                driver.find_element_by_id("checkfp").click()
                logging.info('decode_captcha commit')
                time.sleep(2)

                # 如果验证失败
                if 'popup_message' in driver.page_source:
                    # 如果验证次数过多
                    if '超过该张发票当日查验次数' in driver.page_source:
                        logging.warning('query too much times')
                        return False

                    logging.info('decode_captcha fail, decode again')
                    driver.find_element_by_id("popup_ok").click()
                    time.sleep(1)
                    driver.find_element_by_id("yzm_img").click()
                    time.sleep(3)
                    continue

                def wait2(driver):
                    return '查验时间' in driver.page_source

                WebDriverWait(driver, 10).until(wait2, 'decode_captcha fail to find tax content')
                logging.info('decode_captcha success')
                return True
            except Exception as err:
                logging.exception('decode_captcha error')
                time.sleep(2)
            finally:
                if tmp_driver:
                    logging.info('close selenium driver')
                    tmp_driver.quit()
        return False


# 查询一张发票
def query_one_tax(query_args):
    # logging.info('query_one_tax params[%s]' % query_args)

    # 1.先查历史记录
    row = tools.query_one('api_taxzz_crawled_record', query_args)
    if not row:
        # 2.没有记录再调用爬虫
        # 执行状态 [0:空闲,1:执行中,2:执行成功,-1:执行失败]
        data = {'png_name': '', 'state': 1, 'gfmc_pp': ''}
        data.update(query_args)
        tools.insert_one('api_taxzz_crawled_record', data)
        thread_pool.submit(TaxVeri(query_args).query)
    elif row['state'] == -1:
        tools.update_one('api_taxzz_crawled_record', query_args, {"$set": {"state": 1}})
        thread_pool.submit(TaxVeri(query_args).query)


# 查询一张发票
def query_tax(params):
    logging.info('query_tax params[%s]' % params)
    # if tools.check_params(['tasks'], params):
    #     return query_taxs(params)

    keys = ['fpdm', 'fphm', 'kprq', 'kjje']
    if not tools.check_params(keys, params):
        return tools.getJsonResp(resp=env.RESP_PARAM_ERROR, request_args=params)

    query_args = tools.get_params(keys, params)
    query_one_tax(query_args)
    return query_list(query_args)


'''
# 批量查询发票
def query_taxs(params):
    logging.info('query_taxs params[%s]' % params)
    if not tools.check_params(['tasks'], params):
        return tools.getJsonResp(resp=env.RESP_PARAM_ERROR, request_args=params)

    # 获取tasks数组
    tasks_text = params.get('tasks')
    # 只取一个任务
    task_params = re.compile(r'([\d.]*)?').findall(tasks_text)
    for i in task_params:
        if not i:
            task_params.remove(i)
    logging.info('query_taxs task_params[%s]' % task_params)

    keys = ['fpdm', 'fphm', 'kprq', 'kjje']
    query_args = {}
    query_args_lst = []
    for i in range(len(task_params)):
        query_args[keys[i]] = task_params[i]
    query_args_lst.append(query_args)
    logging.info('query_taxs query_args_lst[%s]' % query_args_lst)

    for i in query_args_lst:
        query_one_tax(i)
    return query_list(query_args)
    # return query_list({})
'''


def query_png(params):
    logging.info('query_png params[%s]' % params)
    png_name = params.get('png_name')
    if not png_name:
        return tools.getJsonResp(resp=env.RESP_PARAM_ERROR, request_args=params)
    try:
        png_path = tools.getSubdir(__file__, 'png') + png_name
        with open(png_path, 'rb') as f:
            resp = make_response(f.read())
            resp.headers['Content-Type'] = 'application/octet-stream'
            resp.headers['Content-Disposition'] = 'attachment;filename=%s' % png_name
            return resp
    except Exception as err:
        logging.error('get_png fail error=%s' % err)
        return str(err)


def query_list(params):
    logging.info('query_list params[%s]' % params)
    rows, keys = tools.query_list_with_keys('api_taxzz_crawled_record', params)
    return render_template("tax_list.html", rows=rows, keys=keys)


if __name__ == '__main__':
    # TaxVeri(fpdm='4403172320', fphm='46746291', kprq='20180325', kjje='668685').query()
    # TaxVeri(fpdm='4403172320', fphm='40535947', kprq='20180513', kjje='967673').query()
    # TaxVeri(fpdm='4403172320', fphm='46547472', kprq='20180505', kjje='441840').query()
    # TaxVeri(fpdm='4403172320', fphm='40535457', kprq='20180429', kjje='742125').query()
    # params = {'fpdm': '4403172320', 'fphm': '46746291', 'kprq': '20180325', 'kjje': '668685'}
    # params = {'fpdm': '4403172320', 'fphm': '40535947', 'kprq': '20180513', 'kjje': '967673'}
    params = {'fpdm': '4403172320', 'fphm': '46547472', 'kprq': '20180505', 'kjje': '441840'}
    tax_veri = TaxVeri(params)
    print(tax_veri.query())
    # print(Recoginze('captcha/b1.png', 8023))
