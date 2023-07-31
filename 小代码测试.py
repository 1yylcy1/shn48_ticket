import requests
from bs4 import BeautifulSoup
import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import hashlib, configparser, re, os, json, random, time, datetime, requests, _thread as thread
import concurrent.futures
# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#-----------------头部数据--------------#
#商城头部   用于验证是否登陆成功，获取页面源代码时用的
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

#登陆头部，登陆时用的
LOGIN_HEADERS = {
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


#登陆数据
login_data = {
    'phone': '',
    'phonecode': '',
    'login_type': '',
    'area': '',
    'preg': '',
    'username': '',
    'password': '',
}
#--------设置一些变量---------#
#获取当前工作目录
ROOT_DIR = os.getcwd()
#登陆日志
LOG_PATH = ROOT_DIR + '\\' + 'log.txt'
COOKIES_PATH = ROOT_DIR + '\\' + 'cookies.txt'

#配置文件路径
CONFIGS_PATH = ROOT_DIR + '\\config.ini'


#-------------类外的一些函数-----------------#
#写入登陆信息的
def logger(*items):
    stringSum = ''
    file = open(LOG_PATH, 'a')
    for item in items:
        stringSum = stringSum + ' ' + str(item)

    print(stringSum)
    logTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]
    file.write(logTime + '   ' + stringSum + '\n')
    file.close()

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
                        response = ses.get(url, headers=headers,verify=False)
        if response.status_code == 200:
            resStatus == False
            return response
    except Exception:
        print("Request  failed!!")

#-------------------------获取切票时间的---------------------------------------------
def getTime():
    tStatus = False
    while tStatus == False:
        ordertime = input("[INPUT-NEEDED] Input order time (in the format at 2020-12-12 19:30:00.00000), Leave empty to use default setting (today's 20:30) :")
        if ordertime == '':
            ordertime = datetime.datetime.now().strftime('%Y-%m-%d') + ' ' + '20:30:00.00000'
        try:
            datetime.datetime.strptime(str(ordertime), '%Y-%m-%d %H:%M:%S.%f')
            tStatus = True
        except Exception:
            logger('[FAIL] Input error occurred, enter again.')
            tStatus = False

    logger('[SUCCESS] Set order time as', ordertime, '\n')
    return ordertime
#----------------------------计算倒计时的-----------------------------
#到时间就自动进行登陆抢票
def countdown(ordertime, leadtime):
    temp = datetime.datetime.strptime(ordertime, '%Y-%m-%d %H:%M:%S.%f')
    lead = datetime.timedelta(seconds=(int(leadtime)))
    loginTime = temp - lead
    loginTime = loginTime.strftime('%Y-%m-%d %H:%M:%S.%f')
    while True:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        if now > loginTime:
            print('Countdown end at', now)
            break
        print('Counting down', now)
        time.sleep(0.01)
#---------------------------------线程锁-----------------------
#创建线程锁
def getLocks(sess):
    locks = []
    for inx in range(0, len(sess)):
        lock = thread.allocate_lock()
        lock.acquire()
        locks.append(lock)

    return locks
#-----------------主要类------------------#
#用来获取配置文件
class getConfigs:

    def __init__(self, filePath):
        #使用 config 对象提供的方法来读取、修改和写入配置文件。
        config = configparser.ConfigParser()
        config.read(filePath, encoding='utf-8')
        self.config = config

    def timeConfigs(self):
        auto = int(self.config.get('delay', 'auto'))
        ticketDelay = float(self.config.get('delay', 'ticketDelay'))
        proxyDelay = float(self.config.get('delay', 'proxyDelay'))
        loopDelay = int(self.config.get('delay', 'loopDelay'))
        return (auto, ticketDelay, proxyDelay, loopDelay)

    def betaConfigs(self):
        msMode = self.config.get('beta', 'msMode')
        timeout = self.config.get('beta', 'timeout')
        return (msMode, timeout)

    def proxiesConfigs(self):
        #useProxies表示是否使用代理服务器的设置，其中 0 可以表示不使用代理，1 可以表示使用代理
        useProxies = int(self.config.get('proxies', 'proxiesSetting'))
        #fixedProxies存储固定代理 IP 地址
        fixedProxies = self.config.get('proxies', 'FixedProxiesIp')
        return (
         useProxies, fixedProxies)
    #获取票的详细信息
    """
    link：场次
    num：每个场次票的数量(一般是1)
    seattype：票的种类（2：vip座  3：普座 4：站座）
    walletPwd：钱包密码
    """
    #获取票的详细信息的 (比较重要)
    def ticketsConfigs(self):
        showId = self.config.get('ticketDetails', 'link').split(',')
        num = self.config.get('ticketDetails', 'num').split(',')
        seattype = self.config.get('ticketDetails', 'seattype').split(',')
        # walletPwds = self.config.get('ticketDetails', 'walletPwd').split(',')
        brandId = self.brandMapping(self.config.get('ticketDetails', 'brandId').split(','))
        #返回一个元组列表
        return (showId, num, seattype, brandId)

    #获取商品的东西的
    def goodsConfigs(self):
        goodsId = self.config.get('goodsDetails', 'link').split(',')
        goodsBrandId = self.brandMapping(self.config.get('goodsDetails', 'brandId').split(','))
        goodNum = self.config.get('goodsDetails', 'goodNum').split(',')
        attrId = self.config.get('goodsDetails', 'attrId').split(',')
        addressID = self.config.get('goodsDetails', 'addressID').split(',')
        lgsId = self.config.get('goodsDetails', 'lgsId').split(',')
        province = self.config.get('goodsDetails', 'province').split(',')
        city = self.config.get('goodsDetails', 'city').split(',')
        return (goodsId, goodsBrandId, goodNum, attrId, addressID, lgsId, province, city)

    def bidConfigs(self):
        bidId = self.config.get('bidDetails', 'link').split('/')[-1]
        priceLimit = int(self.config.get('bidDetails', 'priceLimit'))
        pos = int(self.config.get('bidDetails', 'position'))
        brandIdBid = self.brandMapping(self.config.get('bidDetails', 'brandId'))
        increment = int(self.config.get('bidDetails', 'increment'))
        ocrAppcode = self.config.get('bidDetails', 'ocrAppcode')
        return (bidId, priceLimit, pos, brandIdBid, increment, ocrAppcode)

    #获取用户登陆信息
    def loginConfigs(self):
        user = self.config.get('loginInformation', 'user').split(',')
        pw = self.config.get('loginInformation', 'password').split(',')
        #返回列表元组，第一个列表是用户列表，第二个列表是对应的密码列表
        return (user, pw)


    #用于获取队伍号brand_id的
    def brandMapping(self, brandList):
        numBrandList = []
        for b in brandList:
            s = str(b)
            r = 0
            if s == 'GNZ':
                r = 3
            else:
                if s == 'SNH':
                    r = 1
                else:
                    if s == 'BEJ':
                        r = 2
                    else:
                        if s == 'CKG':
                            r = 5
                        else:
                            if s=='CGT':
                                r=15
            numBrandList.append(r)

        return numBrandList

#-----------------登陆类----------------------#
class login:
    def __init__(self):

        self.login_url='https://user.48.cn/QuickLogin/login/'
        self.shop_url='https://shop.48.cn/home/index'

    # 单次循环登陆函数，如果登不上就一直登陆
    def loginInLoop(self,ses):
        aStatus = False  # 表示登陆状态
        while aStatus == False:
            # 调用单次登陆函数
            aStatus = self.login(ses)
            if aStatus == False:
                logger('[MESSAGE] Try to login again after 3 seconds.')
                time.sleep(3)

    def request_url(self,src,ses):
        res = requestUrl(ses, src, '', SHOP_HEADERS, 'get', False)
        return res

    #单次登陆函数
    def login(self,ses):
        self.ses = ses
        #拿到src属性
        desc = self.ses.post(url=self.login_url, headers=LOGIN_HEADERS, data=login_data).json()['desc']

        # 解析了获取的json文件为类HTML对象
        res = BeautifulSoup(desc, 'html.parser')
        # 查找所有的 <script> 标签，并将它们保存在一个列表 scripts 中
        scripts = res.find_all('script')
        srcs = []
        for script in scripts:
            srcs.append(script['src'])
        #拿到所有srcs
        # print(srcs)

        src_list = []
        #模拟js操作
        for src in srcs:
            ts = getTs()  # 获得一个时间戳
            url = src + '&_=' + str(ts)
            src_list.append(url)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 提交任务并获取Future对象列表
            futures = [executor.submit(self.request_url, src,self.ses) for src in src_list]
            # 获取已完成的任务结果
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        if results[-1].status_code == 200:
            #请求票的商品界面
            res = requestUrl(self.ses,self.shop_url,'',SHOP_HEADERS,'get',False)
            # print(res.text)
            # 拿到shop网页源码，并解析为BeautifulSoup对象
            soup = BeautifulSoup(res.text, 'html.parser')
            # 提取HTML文档中第一个<a>标签内的文本内容
            a = soup.find('a').text
            if a[:2] == '你好':
                print(f"f{login_data['username']}登陆成功！")
                #说明登陆成功
                return True
            else:
                return False
        else:
            print("模拟js失败，请求失败")
            return False

class buy_tickets:
    def __init__(self,ses,showID=None,num=None,seattype=None,brandID=None,user=None):
        self.sess=ses
        self.ticketPostUrl = 'https://shop.48.cn/TOrder/ticket_Add'
        self.showId=showID
        self.num=num
        self.seattype=seattype
        self.brandID=brandID
        self.user=user

        self.choose_times_end = '-1'  # 固定的
        self.ticketstype = '2'  # 好像是固定值
        self.r = random.random  # 随机数

    def buyTicket(self):
        self.TICKET_HEADERS = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'shop.48.cn',
            'Origin': 'https://shop.48.cn',
            'Pragma': 'no-cache',
            'Referer':
                'https://shop.48.cn/tickets/item/' + str(self.showId) + '?seat_type=' + str(self.seattype),
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 Edg/113.0.1774.42',
            'X-Requested-With': 'XMLHttpRequest'
        }
        # 请求的数据
        self.ticket_data = {'ticketsid': self.showId,
                            'num': self.num,
                            'seattype': self.seattype,
                            'brand_id': self.brandID,
                            'choose_times_end': self.choose_times_end,
                            'ticketstype': self.ticketstype,
                            'r': str(self.r)}
        try:
            res = self.sess.post(url=self.ticketPostUrl, data=self.ticket_data, headers=self.TICKET_HEADERS, verify=False)
            if res.json()['Message'] == 'success':
                print(f"用户{self.user}切票成功!")
                return True
            else:
                message=res.json()['Message']
                print(f"用户{self.user}切票失败!  {message}")
                return False
        except:
            print(f"用户{self.user}切票失败!")
            return False


    #规定最多的切票次数
    def buyloop(self, accName,lock):
        """
        accName: str the account name of session for log result
        """
        loopCount = 0
        buyFlag=False#买票状态
        while not buyFlag:
            a = time.time()
            if loopCount >= 0 and loopCount <= 10:
                buyFlag = self.buyTicket()
                loopCount += 1
            else:
                logger('[MESSAGE] Wait ticket function executed 10 times, ending process...')
                break
            #计算切了多久
            b = time.time() - a
            c = 5 - b
            if c > 0:
                logger('[MESSAGE] Wait', c, 'seconds to wait ticket')
                # b = time.time()
                # print(b - a)
                time.sleep(c)
        self.sess.close()
        lock.release()

#---------------------------综合操作---------------------#
def main():
    #创建读取配置文件对象
    gb = getConfigs(CONFIGS_PATH)
    #获取所有登陆用户账号密码
    users, pws = gb.loginConfigs()
    #获取所有登陆用户的票的信息
    showId, num, seattype, brandId=gb.ticketsConfigs()

    # #获取当前时间
    # ordertime = getTime()
    # # 通过倒计时函数进行一段随机长度的倒计时操作。倒计时长度在30到59秒之间
    # countdown(ordertime, 30 + random.randint(0, 29))
    sess = []
    for inx in range(0, len(users)):
        #创建一个会话
        ses = requests.session()
        #创建登陆对象
        a = login()
        #更新用户账号和密码
        login_data['username']=users[inx]
        login_data['password']=pws[inx]
        a.loginInLoop(ses)
        # 保存会话
        sess.append(ses)
    #创建线程锁
    locks = getLocks(sess)
    # 之前已经登陆获取了会话列表sess
    for inx in range(len(sess) - 1, -1, -1):
        #创建买票对象
        b=buy_tickets(sess[inx],showId[inx],num[inx],seattype[inx],brandId[inx],users[inx])
        # 开启一个线程进行抢票
        thread.start_new_thread(b.buyloop, (users[inx], locks[inx]))

    logger('[MESSAGE] ALL DONE')
    time.sleep(30)




    pass
if __name__ == '__main__':
    a=time.time()
    main()

