import requests
import time
import re
import traceback

#服务提供的两个URL
YZM_URL = ["http://dt1.91yzm.com:8080/","http://dt2.91yzm.com:8080/"]
# 账号和密码：
# lls2018/libai2018
# lls2018_u/libai2018

#封装提交和请求，第一个url请求失败，就试图请求第二个url
def Request(url):
    err = "#请求失败"
    for YZM_url in YZM_URL:
        try:
            r = requests.get(YZM_url + url)
            if r.status_code < 300:
                return r.content
            err = "#请求失败," + str(r.status_code)
        except:
            traceback.print_exc()
    return err

def Post(url, data, pic):
    err = "#发送文件失败"
    for YZM_url in YZM_URL:
        try:
            r = requests.post(YZM_url + url, data=data, files=pic)
            if r.status_code < 300:
                result = r.content
                return result
            err = "#发送文件失败," + str(r.status_code)
        except Exception as e:
            traceback.print_exc()
    return err


#发送文件
#auth_code:密码串
#path:文件路径
#dati_type:类型
#timeout:超时时间
#extra_str:备注
#zz:作者
def SendFile(auth_code,path,dati_type,timeout,extra_str,zz=None):
    senddata = {}
    senddata["dati_type"] = dati_type
    senddata["acc_str"] = auth_code
    senddata["timeout"] = timeout
    senddata["extra_str"] = extra_str
    if zz:
        senddata["zz"] = zz
    return Post("uploadpic.php", senddata,{"pic":open(path,"rb")})

#得到答案
def GetAnswer(id):
    return Request("query.php?sid=" + id)

#得到密码串余额
def QueryBalance(auth_code):
    return Request("query.php?action=qmoney&self_authcode=" + auth_code)

#报告错误，当一个识别出错时，提交给服务器说识别出错
def ReportError(auth_code,id):
    return Request("response.php?action=error&auth_code=" + auth_code +"&sid="+id)


#直接识别，返回答案
def Recoginze(path, dati_type, auth_code="Zd0lrHUwwk0ZCjD7", extra_str="备注", timeout=60, zz="lls2018"):
    id = SendFile(auth_code, path, dati_type, timeout, extra_str, zz).decode("gbk")
    if id[0]=='#':
        return -1, id
    time.sleep(2)
    while True:
        answer = GetAnswer(id).decode("gbk")
        if answer!="":
            break
        time.sleep(1)
    return 0, answer


if __name__ == '__main__':
    # while True:
	#     d1 = time.time()
	#     id = SendFile("Zd0lrHUwwk0ZCjD7", r"F:\python_projects\app_h2o\necips_2\captcha\captcha_8a7e0b6c42de11e8a6583c95094bb4f2.png", 8017 , 60,"备注", "lls2018").decode('gbk')
	#     print("1>>> :%s"% id)
	#     while True:
	#         a = GetAnswer("410232350118707599")
	#         if a!="":
	#             break
	#         time.sleep(1)
	#     print ("2>>>>>>>:%s" % a.decode("gbk"))
	#     time.sleep(60)
    path = r"F:\python_projects\app_h2o\necips_2\captcha\captcha_59ccbe743e2911e8ba1f3c95094bb4f2.png"
    dati_type = 8017
    print(Recoginze(path, dati_type))

