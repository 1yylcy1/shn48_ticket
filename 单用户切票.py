import json
import random

import requests
from bs4 import BeautifulSoup
import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import concurrent.futures
import asyncio
import aiohttp



#验证登陆是否成功时，需要获取 网页源代码，请求时用的
SHOP_HEADERS = {
'Accept':
'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'

,'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept - Language':'zh - CN, zh; q = 0.9',
'Cache-Control':'no-cache',
'Connection':'keep-alive',
'Host':'shop.48.cn',
'Origin':'https://shop.48.cn',
'Referer':'https://user.48.cn/',
'Accept-Encoding':'gzip, deflate, br'
}

#将给定的时间参数t转换为毫秒级时间戳
def getTs(t=None):
    if t == None:
        t = time.time()
    else:
        timeArray = time.strptime(t, '%Y-%m-%d %H:%M:%S.%f')
        timestamp = time.mktime(timeArray)
        t = timestamp
    ts = int(round(t * 1000))
    return ts
def requestUrl(ses, url, data, headers, func=None, changeIp=True):
    resStatus = True
    try:
        if func == 'post':
            response = ses.post(url, data=data, headers=headers, verify=False)
        else:
            if func == 'paraGet':
                response = ses.get(url, params=data, headers=headers, verify=False)
            else:
                if func == 'paraPost':
                    response = ses.post(url, params=data, headers=headers,verify=False)
                else:
                    if func == 'get':
                        response = ses.get(url, headers=headers)
        if response.status_code == 200:
            resStatus == False
            return response
    except Exception:
        print("Request  failed!!")
def ticketsConfigs(self):
    showId = self.config.get('ticketDetails', 'link').split(',')
    num = self.config.get('ticketDetails', 'num').split(',')
    seattype = self.config.get('ticketDetails', 'seattype').split(',')
    walletPwds = self.config.get('ticketDetails', 'walletPwd').split(',')
    brandId = self.brandMapping(self.config.get('ticketDetails', 'brandId').split(','))
    return (showId, num, seattype, walletPwds, brandId)
login_headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://user.48.cn',
    'Pragma': 'no-cache',
    'Referer': 'https://user.48.cn/login/index.html',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}
#输入登陆信息
login_data = {
    'phone': '',
    'phonecode': '',
    'login_type': '',
    'area': '',
    'preg': '',
    'username': 'snh480725607396',
    'password': 'qq456789',
}

#desc字段包含多个资源地址
"""
https://live.48.cn/api/uc.php：可能是用于处理直播相关功能的接口。
https://vip.48.cn/api/uc.php：可能是用于处理用户会员相关功能的接口。
https://pay.48.cn/api/uc.ashx：可能是用于处理支付相关功能的接口。
https://shop.48.cn/api/uc.ashx：可能是用于处理商店购物相关功能的接口。
https://m.48.cn/api/uc.ashx：可能是用于处理移动端功能的接口。
https://user.48.cn/api/uc.php：可能是用于处理用户相关功能的接口。
"""
#______________________登陆部分_________________________#
#创建会话
ses = requests.session()
desc = ses.post('https://user.48.cn/QuickLogin/login/', headers=login_headers, data=login_data).json()['desc']

#解析了获取的json文件为类HTML对象
res = BeautifulSoup(desc, 'html.parser')
#查找所有的 <script> 标签，并将它们保存在一个列表 scripts 中
scripts = res.find_all('script')
srcs = []
for script in scripts:
    srcs.append(script['src'])
# print(srcs)
#------5次模拟---------

shopUrl = 'https://shop.48.cn/'
mUrl = 'https://m.48.cn/'
srckeys = [shopUrl, mUrl]
src_list=[]
#--------------多协程处理-----------------

for src in srcs:
    ts = getTs()#获得一个时间戳
    url = src + '&_=' + str(ts)
    src_list.append(url)
a=time.time()
def request_url(src):
    res = requestUrl(ses, src, '', SHOP_HEADERS, 'get', False)
    # 根据需要，你可以在这里对返回结果进行处理
    # print(res)
    return res
# 创建线程池
with concurrent.futures.ThreadPoolExecutor() as executor:
    # 提交任务并获取Future对象列表
    futures = [executor.submit(request_url, src) for src in src_list]

    # 获取已完成的任务结果
    results = [future.result() for future in concurrent.futures.as_completed(futures)]
    print(results[-1].status_code)

b=time.time()
time=b-a
print(time)
#-----------------------多异步协程操作-----------------------------------
# a=time.time()
# async def request_url(session, src):
#     async with session.get(src) as response:
#         res = await response.text()
#         # 根据需要，你可以在这里对返回结果进行处理
#         print(res)
#         return res
# async def requ(session, src_list):
#     tasks = []
#     for src in src_list:
#         task = asyncio.create_task(request_url(session, src))
#         tasks.append(task)
#
#     # 等待所有任务完成
#     results = await asyncio.gather(*tasks)
#     return results
#
# loop = asyncio.get_event_loop()
# aiohttp_session = aiohttp.ClientSession.from_client_session(ses)
# results = loop.run_until_complete(requ(aiohttp_session,src_list))
# loop.close()
# b=time.time()
# time=b-a
# print(time)
#-------------------暴力循环------------------
# a=time.time()
# for src in srcs:
#     #如果是我要的网页链接
#     # if src[:16] in srckeys or src[:19] in srckeys:
#     ts = getTs()#获得一个时间戳
#     url = src + '&_=' + str(ts)
#     res = requestUrl(ses, url, '', SHOP_HEADERS, 'get', False)
# b=time.time()
# time=b-a
# print(time)

shop_url='https://shop.48.cn/home/index'
# ve_log_data={'brand_id': -1,
# 'team_type': -1,
# 'date_type': 0}

res = ses.get(url=shop_url,headers=SHOP_HEADERS,verify=False)
# print(res.text)
# 拿到shop网页源码，并解析为BeautifulSoup对象
soup = BeautifulSoup(res.text, 'html.parser')
# 提取HTML文档中第一个<a>标签内的文本内容
a = soup.find('a').text
if a[:2] == '你好':
    print("登陆成功")
else:
    print("登陆失败")



#---------------------------抢票部分----------------------#
# showId, num, seattype, walletPwds, brandId = ticketsConfigs()
showID='5310'#场次
num='1'#切票数量
seattype='3'#票的种类
brand_id='3'#GNZ


choose_times_end='-1'#固定的
ticketstype='2'#好像是固定值
r=random.random#随机数

ticketPostUrl = 'https://shop.48.cn/TOrder/ticket_Add'
ticket_headers={
'Accept':'application/json, text/javascript, */*; q=0.01',
'Accept-Encoding':'gzip, deflate, br',
'Accept-Language':'zh-CN,zh;q=0.9',
'Cache-Control':'no-cache',
'Connection':'keep-alive',
'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
'Host':'shop.48.cn',
'Origin':'https://shop.48.cn',
'Pragma':'no-cache',
    'Referer':
'https://shop.48.cn/tickets/item/'+str(showID)+'?seat_type='+str(seattype),
'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 Edg/113.0.1774.42',
'X-Requested-With': 'XMLHttpRequest'
}

ticket_data={'ticketsid': showID,
'num': num,
'seattype': seattype,
'brand_id': brand_id,
'choose_times_end': choose_times_end,
'ticketstype': ticketstype,
'r': str(r)}
res=ses.post(url=ticketPostUrl,data=ticket_data,headers=ticket_headers,verify=False)
if res.json()['Message']=='success':
    print("切票成功!")
else:
    a=res.json()['Message']
    print(a)
# print(res.json())
# j=json.load(res.text)
# print()
ses.close()
