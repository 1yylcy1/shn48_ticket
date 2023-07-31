import requests
from bs4 import BeautifulSoup
import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import hashlib, configparser, re, os, json, random, time, datetime, requests, _thread as thread
import concurrent.futures
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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



login_data = {
    'phone': '',
    'phonecode': '',
    'login_type': '',
    'area': '',
    'preg': '',
    'username': '',
    'password': '',
}
ROOT_DIR = os.getcwd()
LOG_PATH = ROOT_DIR + '\\' + 'log.txt'
COOKIES_PATH = ROOT_DIR + '\\' + 'cookies.txt'
CONFIGS_PATH = ROOT_DIR + '\\config.ini'
def logger(*items):
    stringSum = ''
    file = open(LOG_PATH, 'a')
    for item in items:
        stringSum = stringSum + ' ' + str(item)

    print(stringSum)
    logTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]
    file.write(logTime + '   ' + stringSum + '\n')
    file.close()
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
def getLocks(sess):
    locks = []
    for inx in range(0, len(sess)):
        lock = thread.allocate_lock()
        lock.acquire()
        locks.append(lock)

    return locks
class getConfigs:

    def __init__(self, filePath):

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

        useProxies = int(self.config.get('proxies', 'proxiesSetting'))

        fixedProxies = self.config.get('proxies', 'FixedProxiesIp')
        return (
         useProxies, fixedProxies)
    def ticketsConfigs(self):
        showId = self.config.get('ticketDetails', 'link').split(',')
        num = self.config.get('ticketDetails', 'num').split(',')
        seattype = self.config.get('ticketDetails', 'seattype').split(',')
        # walletPwds = self.config.get('ticketDetails', 'walletPwd').split(',')
        brandId = self.brandMapping(self.config.get('ticketDetails', 'brandId').split(','))

        return (showId, num, seattype, brandId)
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
    def loginConfigs(self):
        user = self.config.get('loginInformation', 'user').split(',')
        pw = self.config.get('loginInformation', 'password').split(',')

        return (user, pw)
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
class login:
    def __init__(self):

        self.login_url='https://user.48.cn/QuickLogin/login/'
        self.shop_url='https://shop.48.cn/home/index'


    def loginInLoop(self,ses):
        aStatus = False
        while aStatus == False:

            aStatus = self.login(ses)
            if aStatus == False:
                logger('[MESSAGE] Try to login again after 3 seconds.')
                time.sleep(3)

    def request_url(self,src,ses):
        res = requestUrl(ses, src, '', SHOP_HEADERS, 'get', False)
        return res
    def login(self,ses):
        self.ses = ses
        desc = self.ses.post(url=self.login_url, headers=LOGIN_HEADERS, data=login_data).json()['desc']
        res = BeautifulSoup(desc, 'html.parser')
        scripts = res.find_all('script')
        srcs = []
        for script in scripts:
            srcs.append(script['src'])
        src_list = []
        for src in srcs:
            ts = getTs()
            url = src + '&_=' + str(ts)
            src_list.append(url)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.request_url, src,self.ses) for src in src_list]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        if results[-1].status_code == 200:
            res = requestUrl(self.ses,self.shop_url,'',SHOP_HEADERS,'get',False)
            soup = BeautifulSoup(res.text, 'html.parser')
            a = soup.find('a').text
            if a[:2] == '你好':
                print(f"f{login_data['username']}login successfully！")
                return True
            else:
                return False
        else:
            print("request failed!")
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
        self.choose_times_end = '-1'
        self.ticketstype = '2'
        self.r = random.random

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
                print(f"user{self.user}ticket successfully!")
                return True
            else:
                message=res.json()['Message']
                print(f"user{self.user}ticket failed!  {message}")
                return False
        except:
            print(f"user{self.user}ticket successfully!")
            return False
    def buyloop(self, accName,lock):
        """
        accName: str the account name of session for log result
        """
        loopCount = 0
        buyFlag=False
        while not buyFlag:
            a = time.time()
            if loopCount >= 0 and loopCount <= 10:
                buyFlag = self.buyTicket()
                loopCount += 1
            else:
                logger('[MESSAGE] Wait ticket function executed 10 times, ending process...')
                break
            b = time.time() - a
            c = 5 - b
            if c > 0:
                logger('[MESSAGE] Wait', c, 'seconds to wait ticket')
                # b = time.time()
                # print(b - a)
                time.sleep(c)
        self.sess.close()
        lock.release()
def main():
    gb = getConfigs(CONFIGS_PATH)
    users, pws = gb.loginConfigs()
    showId, num, seattype, brandId=gb.ticketsConfigs()
    ordertime = getTime()
    countdown(ordertime, 30 + random.randint(0, 29))
    sess = []
    for inx in range(0, len(users)):
        ses = requests.session()
        a = login()
        login_data['username']=users[inx]
        login_data['password']=pws[inx]
        a.loginInLoop(ses)
        sess.append(ses)
    locks = getLocks(sess)
    for inx in range(len(sess) - 1, -1, -1):
        b=buy_tickets(sess[inx],showId[inx],num[inx],seattype[inx],brandId[inx],users[inx])
        thread.start_new_thread(b.buyloop, (users[inx], locks[inx]))
    logger('[MESSAGE] ALL DONE')
    time.sleep(30)
if __name__ == '__main__':
    # a=time.time()
    main()

