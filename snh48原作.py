import hashlib, configparser, re, os, json, random, time, datetime, requests, _thread as thread
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#获取当前工作目录
ROOT_DIR = os.getcwd()
#登陆日志
LOG_PATH = ROOT_DIR + '\\' + 'log.txt'
COOKIES_PATH = ROOT_DIR + '\\' + 'cookies.txt'
CONFIGS_PATH = ROOT_DIR + '\\config.ini'
LOOP_DELAY = 1
TIMEOUT = 30
USE_PROXIES = 0
FIXED_PROXIES = {}
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
    'sec-ch-ua-platform': '"Windows"',}
SHOP_HEADERS = {
 'Accept': "'*/*'",
 'Accept-Encoding': "'gzip, deflate, br'",
 'Accept-Language': "'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,zh-TW;q=0.6,ja;q=0.5'",
 'Connection': "'keep-alive'",
 'Host': "'shop.48.cn'",
 'Sec-Fetch-Dest': "'script'",
 'Sec-Fetch-Mode': "'no-cors'",
 'Sec-Fetch-Site': "'same-site'",
 'User-Agent': "'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'"}
M_HEADERS = {
 'Accept': "'*/*'",
 'Accept-Encoding': "'gzip, deflate, br'",
 'Accept-Language': "'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,zh-TW;q=0.6,ja;q=0.5'",
 'Connection': "'keep-alive'",
 'Host': "'m.48.cn'",
 'Sec-Fetch-Dest': "'script'",
 'Sec-Fetch-Mode': "'no-cors'",
 'Sec-Fetch-Site': "'same-site'",
 'User-Agent': "'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'"}
OCR_HEADERS = {'Authorization':'APPCODE ',
 'Content-Type':'application/json; charset=UTF-8'}

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
    def ticketsConfigs(self):
        showId = self.config.get('ticketDetails', 'link').split(',')
        num = self.config.get('ticketDetails', 'num').split(',')
        seattype = self.config.get('ticketDetails', 'seattype').split(',')
        walletPwds = self.config.get('ticketDetails', 'walletPwd').split(',')
        brandId = self.brandMapping(self.config.get('ticketDetails', 'brandId').split(','))
        return (showId, num, seattype, walletPwds, brandId)

    #获取
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
            numBrandList.append(r)

        return numBrandList


class getProxy:

    def __init__(self, useProxies, fixedProxies, wanbianAppid=None, wanbianAppkey=None):
        self.useProxies = useProxies
        self.wanbianAppid = wanbianAppid
        self.wanbianAppkey = wanbianAppkey
        self.fixedProxies = fixedProxies#固定代理
        self.proxyPoolRedisUrl = 'http://localhost:5555/random'
        self.checkIpUrl = 'https://ifconfig.co/'
        self.wanbianUrl = 'http://ip.ipjldl.com/index.php/api/entry?'
        self.wanbianData = {
         'method': "'proxyServer.tiqu_api_url'",
         'packid': 0,
         'fa': 0,
         'dt': "''",
         'groupid': 0,
         'fetch_key': "''",
         'qty': 1,
         'time': 2,
         'port': 1,
         'format': "'txt'",
         'ss': 1,
         'css': "''",
         'pro': "''",
         'city': "''",
         'usertype': 6}
        self.wanbianGetWlUrl = 'https://www.wanbianip.com/Users-whiteIpListNew.html?'
        self.wanbianAddWlUrl = 'https://www.wanbianip.com/Users-whiteIpAddNew.html?'
        self.wanbianDelWlUrl = 'https://www.wanbianip.com/Users-whiteIpDelNew.html?'
        self.wanbianBalWlUrl = 'https://www.wanbianip.com/Users-getBalanceNew.html?'

    def getProxyFromWanbian(self):
        url = self.getDataSumUrl(self.wanbianData, self.wanbianUrl)
        proxies = {'http':'http://127.0.0.1:8080',  'https':'http://127.0.0.1:8080'}
        if self.useProxies == 1:
            if self.fixedProxies == '':
                logger('[MESSAGE] Get proxies from wanbian...')
                while proxies['http'] == '' or proxies['http'] == None:
                    proxies = self.getProxyInLoop(url)
                    proxies = self.proxyInDict(proxies)

                return proxies
            logger('[MESSAGE] Use fixed proxies...')
            return self.proxyInDict(self.fixedProxies)
        else:
            logger('[MESSAGE] Execute without proxies...')
            return proxies

    def getDataSumUrl(self, dataDict, baseUrl):
        dataSum = ''
        for key, item in dataDict.items():
            dataSum = dataSum + '&' + key + '=' + str(item)

        url = baseUrl + dataSum
        return url

    def getProxyFromPool(self, poolUrl):
        try:
            response = requests.get(poolUrl)
            if response.status_code == 200:
                return response.text
        except Exception:
            return

    def getProxyInLoop(self, poolUrl):
        temp = self.getProxyFromPool(poolUrl)
        if temp is not None:
            logger('[SUCCESS] Get proxies successfully. The proxy settings is', temp)
            return temp
        logger('[FAIL] Fail to get proxies.')
        return

    def proxyInDict(self, s):
        proxiesDict = {'http':s,
         'https':s}
        return proxiesDict

    def getMyIp(self):
        res = requests.get((self.checkIpUrl), verify=False)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            ip = soup.find('code', {'class': 'ip'}).text
            logger('[SUCCESS] Get local ip:', ip)
            return ip
        logger('[FAIL] Fail to get local ip')
        return False

    def addWhitelistWanbian(self):
        logger('[MESSAGE] Try to add local ip to wanbian whitelist')
        if self.wanbianAppid != '' and self.wanbianAppkey != '':
            data = {'appid':self.wanbianAppid,  'appkey':self.wanbianAppkey}
            try:
                res = requests.get((self.getDataSumUrl(data, self.wanbianBalWlUrl)), verify=False)
                bal = json.loads(res.text)['data']
                logger('[MESSAGE] Getting current balance in wanbian, the balance is:', bal)
                res = requests.get((self.getDataSumUrl(data, self.wanbianGetWlUrl)), verify=False)
                currentWhitelist = json.loads(res.text)['data']
                logger('[MESSAGE] Getting current whitelist in wanbian, the current whitelist is:', currentWhitelist)
                for ip in currentWhitelist:
                    data['whiteip'] = ip
                    res = requests.get((self.getDataSumUrl(data, self.wanbianDelWlUrl)), verify=False)
                    logger('[MESSAGE] Empting the whitelist, the result is:', res.text)

                data['whiteip'] = self.getMyIp()
                res = requests.get((self.getDataSumUrl(data, self.wanbianAddWlUrl)), verify=False)
                logger('[MESSAGE] Adding local ip to whitelist, the result is:', res.text, '\n')
            except Exception:
                logger('[MESSAGE] Fail to add local ip to wanbian whitelist. Execute without add whitelist\n')

        else:
            logger('[FAIL] appid and appkey are not exist. Execute without add whitelist\n')


class login:

    def __init__(self, user, pw, ses, proxies, msMode):
        self.loginHeaders = LOGIN_HEADERS
        self.shopHeaders = SHOP_HEADERS
        self.mHeaders = M_HEADERS
        self.shopUrl = 'https://shop.48.cn/'
        self.mUrl = 'https://m.48.cn/'
        self.loginUrl = 'https://user.48.cn/QuickLogin/login/'
        self.user = user
        self.pw = pw
        self.ses = ses
        self.proxies = proxies
        self.msMode = msMode

    #循环登陆函数，如果登不上就一直登陆
    def loginInLoop(self):
        aStatus = False#表示登陆状态
        while aStatus == False:
            #调用单次登陆函数
            aStatus = self.login()
            if aStatus == False:
                logger('[MESSAGE] Try to login again after 5 seconds.')
                time.sleep(5)

    def login(self):
        #Try to login as self.user
        logger('[MESSAGE] Try to login as', self.user)
        desc = self.loginPostUrl()#拿到src
        srcs = self.descHandler(desc)#srcs是一个48功能网址列表

        #循环登陆网址
        self.shopLoginPostUrl(srcs)
        #self.msMode默认为s，如果为True说明登陆成功了，login函数返回True
        if self.checkShopStatus(self.msMode) == True:
            logger('[SUCCESS] Login status check success.')
            return True
        logger('[FAIL] Login status check fail.')
        return False

    def checkShopStatus(self, domin):
        if domin == 'm':
            logger('[MESSAGE] Check login status at domin', self.mUrl)#出问题的地方
            res, self.proxies = requestUrl(self.ses, self.mUrl, '', self.mHeaders, self.proxies, 'get', False)
            soup = BeautifulSoup(res.text, 'html.parser')
            a = soup.find('a', {'class': 'iconfont_s con_enter fs26'})
            if a != None:
                return True
        else:
            logger('[MESSAGE] Check login status at domin', self.shopUrl)
            #拿到响应和代理
            res, self.proxies = requestUrl(self.ses, self.shopUrl, '', self.shopHeaders, self.proxies, 'get', False)
            #拿到shop网页源码，并解析为BeautifulSoup对象
            soup = BeautifulSoup(res.text, 'html.parser')
            #提取HTML文档中第一个<a>标签内的文本内容
            a = soup.find('a').text
            if a[:2] == '你好':
                return True
        return False

    def loginPostUrl(self):
        data = {'phone':'""',
         'phonecode':'""',
         'login_type':'""',
         'area':'""',
         'preg':'""',
         'username':self.user,
         'password':self.pw}
        #向登陆界面发送请求，请求方式为POST，res为响应
        res, self.proxies = requestUrl(self.ses, self.loginUrl, data, self.loginHeaders, self.proxies, 'post', False)
        if res.status_code == 200:
            logger('[MESSAGE] Post login request successfully.')
            j = json.loads(res.text)['desc']
            return j
        logger('[MESSAGE] Fail to post login request.')
        logger(logger(res.text))

    def shopLoginPostUrl(self, srcs):
        srckeys = [
         self.shopUrl, self.mUrl]
        #暴力循环找切票请求url
        for src in srcs:
            # if src[:16] in srckeys or src[:19] in srckeys:
            ts = getTs()#获取时间戳
            url = src + '&_=' + str(ts)
            #拿到shop界面的resposne
            res, self.proxies = requestUrl(self.ses, url, '', self.shopHeaders, self.proxies, 'get', False)

    def descHandler(self, desc):
        soup = BeautifulSoup(desc, 'html.parser')
        scripts = soup.find_all('script')
        srcs = []
        for script in scripts:
            srcs.append(script['src'])

        return srcs


class buyTicket:

    def __init__(self, ses, proxies, walletPwd=None, showId=None, num=None, seattype=None, brandId=None, msMode='s'):
        if msMode == 'm':
            self.shopHeaders = M_HEADERS
            self.ticketPostUrl = 'https://m.48.cn/TOrder/add'
            self.ticketStatusUrl = 'https://m.48.cn/torder/GetData?pageindex=1&pagesize=15&order_status=-1&seldate=30'
            self.ticketWaitUrl = 'https://m.48.cn/TOrder/wait'
        else:
            self.shopHeaders = SHOP_HEADERS
            self.ticketPostUrl = 'https://shop.48.cn/TOrder/add'
            self.ticketWaitUrl = 'https://shop.48.cn/TOrder/wait'
        if walletPwd != None:
            self.walletPwd = hashlib.md5(walletPwd.encode(encoding='UTF-8')).hexdigest()
        #准备参数
        self.ses = ses
        self.proxies = proxies
        self.showId = showId
        self.num = num
        self.seattype = seattype
        self.brandId = brandId

    def buyloop(self, accName, lock):
        """
        accName: str the account name of session for log result
        """
        loopCount = 0
        while 1:
            a = time.time()
            if loopCount == 0:
                buyFlag = self.buyTicket()
                loopCount += 1
            else:
                if loopCount != 0 and loopCount <= 10:
                    buyFlag = self.buyTicket(True)
                else:
                    logger('[MESSAGE] Wait ticket function executed 10 times, ending process...')
                    break
            #计算切了多久
            b = time.time() - a
            c = 10 - b
            if c > 0:
                logger('[MESSAGE] Wait', c, 'seconds to wait ticket')
                time.sleep(c)

        lock.release()

    #d是切票行为之后的网页json文件
    def orderResultHandle(self, d):
        try:
            code = ''
            status = d['HasError']
            if status == False:
                code = 'success'
            else:
                code = d['ErrorCode']
            return code
        except Exception as e:
            try:
                return e
            finally:
                e = None
                del e

    def buyTicket(self, wait=False):
        #拿到切票行为后的网页json数据
        dictResult = self.buyTicketPostUrl(wait)
        logger('[MESSAGE] Order sent at', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        resultCode = self.orderResultHandle(dictResult)#检查切票是否成功
        if resultCode == 'success':
            logger('[SUCCESS] Order sent successfully. The id of the show is', self.showId)
            return True
        logger('[FAIL] Fail to order ticket, the error code is', resultCode, ', with error massage as', dictResult)
        return False

    def buyTicketPostUrl(self, wait=False):
        r = random.random()
        if wait == False:
            #self.ticketPostUrl = 'https://shop.48.cn/TOrder/add'
            url = self.ticketPostUrl
            data = {'id':self.showId,  'num':self.num,  'seattype':self.seattype,  'brand_id':self.brandId,  'r':r,  'choose_times_end':-1}
        else:
            if wait == True:
                url = self.ticketWaitUrl
                data = {'id':self.showId,  'num':1,  'seattype':self.seattype,  'brand_id':self.brandId,  'pwd':self.walletPwd,  'r':r}
        #res就是response
        res, self.proxies = requestUrl(self.ses, url, data, self.shopHeaders, self.proxies, 'post', False)
        print("response状态：",res)
        j = resHandler(res.text)
        return j


class buyGood:

    def __init__(self, ses, proxies, goodsId=None, goodsBrandId=None, goodNum=None, attrId=None, addressID=None, lgsId=None, province=None, city=None, msMode='m'):
        if msMode == 'm':
            self.shopHeaders = M_HEADERS
            self.ticketPostUrl = 'https://m.48.cn/TOrder/add'
            self.goodsLimitUrl = 'https://m.48.cn/order/limited'
            self.goodsGetFareNew = 'https://m.48.cn/order/getFareNew'
            self.goodsAddPostUrl = 'https://m.48.cn/order/buy'
            self.goodsBuyPostUrl = 'https://m.48.cn/Order/BuySaveForGive'
            self.ticketRootUrl = 'https://m.48.cn/tickets/item/'
            self.ticketStatusUrl = 'https://m.48.cn/torder/GetData?pageindex=1&pagesize=15&order_status=-1&seldate=30'
            self.ticketWaitUrl = 'https://m.48.cn/TOrder/wait'
        else:
            self.shopHeaders = SHOP_HEADERS
            self.ticketPostUrl = 'https://shop.48.cn/TOrder/add'
            self.goodsLimitUrl = 'https://shop.48.cn/order/limited'
            self.goodsGetFareNew = 'https://shop.48.cn/order/getFareNew'
            self.goodsAddPostUrl = 'https://shop.48.cn/order/buy'
            self.goodsBuyPostUrl = 'https://shop.48.cn/Order/BuySaveForGive'
            self.ticketRootUrl = 'https://shop.48.cn/tickets/item/'
            self.ticketStatusUrl = 'https://shop.48.cn/torder/GetData?pageindex=1&pagesize=15&order_status=-1&seldate=30'
            self.ticketWaitUrl = 'https://shop.48.cn/TOrder/wait'
        self.ses = ses
        self.proxies = proxies
        self.goodsId = goodsId
        self.goodsBrandId = goodsBrandId
        self.addressID = addressID
        self.attrId = attrId
        self.goodNum = goodNum
        self.lgsId = lgsId
        self.province = province
        self.city = city

    def goodloop(self, accName, lock):
        """
        accName: str the account name of session for log result
        """
        loopCount = 0
        while True:
            buyFlag = self.buyGoods()
            if buyFlag == False:
                loopCount += 1
                if loopCount >= 5:
                    logger('[MESSAGE] Executed 5 times on account of', accName, ', sleep 10 seconds before next try')
                    time.sleep(10)
                    loopCount = 0
                else:
                    ldr = loopDelayRand()
                    logger('[FAIL] Execute result is', buyFlag, ', sleep', ldr, 'seconds before next try. Account name is', accName)
                    time.sleep(ldr)
            else:
                logger('[SUCCESS] Execute result is', buyFlag, ', thread ended. Account name is', accName)
                break

        lock.release()

    def orderResultHandle(self, d):
        try:
            code = ''
            status = d['HasError']
            if status == False:
                code = 'success'
            else:
                code = d['ErrorCode']
            return code
        except Exception as e:
            try:
                return e
            finally:
                e = None
                del e

    def buyGoods(self):
        orderLimitResult = self.orderLimited()#拿到切票成功后加载的json数据
        resultCode = self.orderResultHandle(orderLimitResult)
        if resultCode != 'success':
            logger('[FAIL] Goods order fail to deliver. Failure details are:')
            logger(orderLimitResult)
            return False
        pageContent = self.addToCart()
        goodsElem = self.goodsOrderPageHandle(pageContent)
        goodsElem = self.getFare(goodsElem)
        dictResult = self.buyGoodsPostUrl(goodsElem)
        logger('[MESSAGE] Order sent at', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        resultCode = self.orderResultHandle(dictResult)
        if resultCode == 'success':
            logger('[SUCCESS] Goods order sent successfully')
            return True
        logger('[FAIL] Goods order fail to deliver. Failure details are:', dictResult)
        return False

    def orderLimited(self):
        data = {'goods_id':self.goodsId,
         'attr_id':self.attrId,  'num':self.goodNum,  'isLoadCardNum':'true',  'brand_id':self.goodsBrandId}
        res, self.proxies = requestUrl(self.ses, self.goodsLimitUrl, data, self.shopHeaders, self.proxies, 'post', False)
        j = resHandler(res.text)
        return j

    def addToCart(self):
        data = {'num':self.goodNum,
         'donatenum':0,  'goods_id':self.goodsId,  'ext_id':0,  'attr_id':self.attrId}
        res, self.proxies = requestUrl(self.ses, self.goodsAddPostUrl, data, self.shopHeaders, self.proxies, 'post', False)
        pageContent = res.text
        return pageContent

    def goodsOrderPageHandle(self, pageContent):
        temp = {}
        try:
            soup = BeautifulSoup(pageContent, 'html.parser')
            elems = soup.find_all('input')
        except Exception:
            return temp
        else:
            for elem in elems:
                try:
                    temp[elem['id']] = elem['value']
                except Exception:
                    pass

            return temp

    def getFare(self, d):
        try:
            data = {'page_source':d['page_source'],  'cart_id':'',
             'goods_id':d['goods_id'],
             'attr_id':d['attr_id'],
             'num':d['num'],
             'province':self.province,
             'city':self.city,
             'lgs_id':self.lgsId}
            res, self.proxies = requestUrl(self.ses, self.goodsGetFareNew, data, self.shopHeaders, self.proxies, 'post', False)
            j = resHandler(res.text)
            fare = j['fare']
            d['shipping_fee'] = fare
            d['IsIntegralOffsetFreight'] = 'false'
            d['sumPayPrice'] = float(d['goods_amount']) + float(fare)
            return d
        except Exception:
            return d

    def buyGoodsPostUrl(self, goodsElem):
        r = random.random()
        data = {
         'AddressID': "''",
         'goods_amount': "''",
         'shipping_fee': "''",
         'goods_id': "''",
         'attr_id': "''",
         'num': "''",
         'sumPayPrice': "''",
         'is_inv': "''",
         'lgs_id': "''",
         'integral': "''",
         'invoice_type': "''",
         'invoice_title': "''",
         'invoice_price': "''",
         'CompanyName': "''",
         'TaxpayerID': "''",
         'CompanyAddress': "''",
         'CompanyPhone': "''",
         'CompanyBankOfDeposit': "''",
         'CompanyBankNo': "''",
         'rule_goodslist_content': "''",
         'radom_rule_goodslist_content': "''",
         'remark': "''",
         'IsIntegralOffsetFreight': "''",
         'ruleGoodsContent': "''",
         'ruleGoodsContentSign': "''",
         'r': 'r'}
        data['AddressID'] = self.addressID
        data['lgs_id'] = self.lgsId
        data['is_inv'] = 'false'
        data['invoice_title'] = 'anon'
        data['invoice_price'] = '0'
        keys = data.keys()
        for key in keys:
            try:
                data[key] = goodsElem[key]
            except Exception:
                continue

        res, self.proxies = requestUrl(self.ses, self.goodsBuyPostUrl, data, self.shopHeaders, self.proxies, 'post', False)
        j = resHandler(res.text)
        return j


class bid:

    def __init__(self, ses, proxies, bidId, priceLimit, pos, brandIdBid, increment, ocrAppcode, msMode):
        if msMode == 'm':
            self.shopHeaders = M_HEADERS
            self.checkUserUrl = 'https://m.48.cn/pai/CheckUserInfo/'
            self.bidPost = 'https://m.48.cn/pai/ToBids/'
            self.checkPricesUrl = 'https://m.48.cn/pai/GetShowBids'
            self.getImageUrl = 'https://m.48.cn/VerifyCode/VerificationCodeImage'
            self.checkImageUrl = 'https://m.48.cn/VerifyCode/VerificationCheck'
        else:
            self.shopHeaders = SHOP_HEADERS
            self.checkUserUrl = 'https://shop.48.cn/pai/CheckUserInfo/'
            self.bidPost = 'https://shop.48.cn/pai/ToBids/'
            self.checkPricesUrl = 'https://shop.48.cn/pai/GetShowBids'
            self.getImageUrl = 'https://shop.48.cn/VerifyCode/VerificationCodeImage'
            self.checkImageUrl = 'https://shop.48.cn/VerifyCode/VerificationCheck'
        self.msMode = msMode
        self.bidId = bidId
        self.shopHeaders['Referer'] = 'https://shop.48.cn/pai/item/' + str(self.bidId)
        self.priceLimit = priceLimit
        self.pos = pos
        self.brandIdBid = brandIdBid
        self.increment = increment
        self.ses = ses
        self.proxies = proxies
        self.sleeptimeForBid = 0.2
        self.ocrUrl = 'http://tysbgpu.market.alicloudapi.com/api/predict/ocr_general'
        OCR_HEADERS['Authorization'] = 'APPCODE ' + ocrAppcode
        self.ocrHeaders = OCR_HEADERS

    def bid(self):
        cStatus = True
        while cStatus == True:
            j = self.checkUser()
            cStatus = j['retValue']['HasError']
            if cStatus == True:
                logger('[FAIL] Bid user info check fail.', j)
                try:
                    depositStatus = str(j['retValue']['Message'])
                    if depositStatus == '':
                        break
                except Exception:
                    pass

                tempInput = str(input('[INPUT-NEEDED] Press c to continue'))
                if tempInput == 'c':
                    break
                time.sleep(self.sleeptimeForBid)

        logger('[MESSAGE] Bid user info check ended.')
        myPrice = 0
        successPrice = 0
        methodFlag = 0
        while 1:
            bidDict = {'list': []}
            for page in range(0, 100):
                temp = self.getBidHistory(page)
                if len(temp['list']) != 0:
                    bidDict['list'].extend(temp['list'])
                    if temp['list'][-1]['bid_amt'] < successPrice:
                        logger('[MESSAGE] Stop to get historical bid prices after page', page)
                        break
                    ldr = loopDelayRand()
                    time.sleep(ldr)
                    logger('[MESSAGE] Sleep ', ldr, 'seconds to get price in next page')
                else:
                    logger('[MESSAGE] Reach the end of historical prices at page', page - 1)
                    break

            time.sleep(self.sleeptimeForBid)
            currentPrice = self.getCurrentPrice(bidDict)
            if currentPrice != False:
                logger('[MESSAGE] Get current price as', currentPrice, 'at position', self.pos)
            else:
                logger('[MESSAGE] Error occured when trying to handle bidDict, try to get price again')
                continue
            if successPrice < currentPrice:
                if currentPrice - successPrice > self.increment:
                    myPrice = currentPrice + random.randint(2, self.increment)
                else:
                    myPrice = currentPrice + self.increment
                while myPrice > self.priceLimit:
                    self.priceLimit = self.setNewPrice()

                logger('[MESSAGE] Set new price as', myPrice)
                if methodFlag == 0:
                    bidResult = self.postNewPrice(myPrice)
                    if bidResult['HasError'] == True:
                        logger('[FAIL] Fail to send new price. Error details are:', bidResult)
                        methodCheck = str(input('[INPUT-NEEDED] Press c to use bid method of the one with code image,leave empty to countine bidding without code image.'))
                        if methodCheck == 'c':
                            logger('[MESSAGE] Use bid method of the one with code image')
                            methodFlag = 1
                        else:
                            logger('[MESSAGE] Continue bidding without code image')
                            methodFlag = 0
                    else:
                        successPrice = myPrice
                        logger('[SUCCESS] New price sent successfully. The new price is', successPrice, '\nThe bidResult is', bidResult)
            elif methodFlag == 1:
                bidResult = self.postWithImageCode(myPrice)
                if bidResult['status'] != 'ok':
                    logger('[FAIL] Fail to send new price. Error details are:', bidResult)
                else:
                    successPrice = myPrice
                    logger('[SUCCESS] New price sent successfully. The new price is', successPrice, '\nThe bidResult is', bidResult)

    def postWithImageCode(self, amt):
        bidRes = False
        while bidRes == False:
            data = {'id': int(self.bidId)}
            if self.msMode == 'm':
                res, self.proxies = requestUrl(self.ses, self.getImageUrl, data, self.shopHeaders, self.proxies, 'paraGet', False)
            else:
                res, self.proxies = requestUrl(self.ses, self.getImageUrl, data, self.shopHeaders, self.proxies, 'paraPost', False)
            try:
                res = eval(res.text)
                imgBase64 = res['result'].split(',')[-1]
                imgMsg = res['msg']
                pattern = re.compile('[【](.*)[】]')
                msg = re.findall(pattern, imgMsg)
                msg = msg[0]
            except Exception as e:
                try:
                    logger('[MESSAGE] Failure occured when handling imgdata form 48. Error message is', e)
                    continue
                finally:
                    e = None
                    del e

            logger('[MESSAGE] Get image successfully, the img word msg is', msg)
            ocrRes = self.getOcrResults(imgBase64)
            if ocrRes != False:
                wordsPos = self.getPositionFromOcr(msg, ocrRes)
                if wordsPos != False:
                    data = {'code':str(wordsPos).replace(' ', ''),
                     'id':int(self.bidId),
                     'amt':int(amt),
                     'num':1}
                    res, self.proxies = requestUrl(self.ses, self.checkImageUrl, data, self.shopHeaders, self.proxies, 'paraPost', False)
                    bidRes = resHandler(res.text)
                    logger('[MESSAGE] Image code bidding result is,', bidRes)
                    try:
                        if bidRes['status'] == 'error':
                            bidRes = False
                    except Exception as e:
                        try:
                            bidRes = False
                        finally:
                            e = None
                            del e

            else:
                logger('[MESSAGE] ocrRes is False, error details are', ocrRes)

        return bidRes

    def getOcrResults(self, imgBase64):
        ocrData = {'image':imgBase64,
         'configure':{
          'min_size': 20,
          'output_prob': True,
          'output_keypoints': False,
          'skip_detection': False,
          'without_predicting_direction': False,
          'language': "'sx'"}}
        try:
            ocrDataJson = json.dumps(ocrData)
            res, self.proxies = requestUrl(self.ses, self.ocrUrl, ocrDataJson, self.ocrHeaders, self.proxies, 'post', False)
            j = resHandler(res.text)
            if j['success'] == True:
                return j['ret']
            return False
        except Exception as e:
            try:
                logger('[MESSAGE] Failure occured when trying to get ocr results. Error message is', e)
                return False
            finally:
                e = None
                del e

    def getPositionFromOcr(self, words, ocrRes):
        wordsPos = []
        for word in words:
            for ocr in ocrRes:
                ocrWord = ocr['word']
                if word in ocrWord:
                    rect = ocr['rect']
                    left = rect['left']
                    width = rect['width']
                    top = rect['top']
                    height = rect['height']
                    if len(ocrWord) == 1:
                        x = left + width / 2
                        y = top + height / 2
                    else:
                        partWidth = width / len(ocrWord)
                        partHeight = height / len(ocrWord)
                        inx = ocrWord.find(word) + 1
                        x = left + partWidth * inx / 2
                        y = top + partHeight * inx / 2
                    temp = {'_X':int(x),
                     '_Y':int(y)}
                    wordsPos.append(temp)

        if len(wordsPos) == len(words):
            return wordsPos
        return False

    def checkUser(self):
        j = False
        while j == False:
            r = random.random()
            data = {'id':self.bidId,
             'brand_id':self.brandIdBid,
             'r':r}
            res, self.proxies = requestUrl(self.ses, self.checkUserUrl, data, self.shopHeaders, self.proxies, 'post', False)
            j = resHandler(res.text)

        return j

    def postNewPrice(self, np):
        j = False
        while j == False:
            r = random.random()
            data = {'id':self.bidId,
             'amt':np,
             'num':1,
             'code':'',
             'r':r}
            res, self.proxies = requestUrl(self.ses, self.bidPost, data, self.shopHeaders, self.proxies, 'post', False)
            j = resHandler(res.text)

        return j

    def setNewPrice(self):
        try:
            newPrice = int(input('[INPUT-NEEDED] The bid price is over limit ,enter a new price to proceed bidding:'))
            return newPrice
        except Exception:
            logger('[MESSAGE] Invaild input')
            self.setNewPrice()

    def getBidHistory(self, pageNum):
        j = False
        while j == False:
            r = random.random()
            data = {'id':self.bidId,  'numPerPage':20,  'pageNum':pageNum,  'r':r}
            res, self.proxies = requestUrl(self.ses, self.checkPricesUrl, data, self.shopHeaders, self.proxies, 'paraPost', False)
            j = resHandler(res.text)

        return j

    def getCurrentPrice(self, d):
        bidData = d['list']
        bidList = []
        lastPrice = 0
        for i in range(0, len(bidData)):
            temp = bidData[i]
            if temp['auction_status'] == 1:
                bidList.append(temp['bid_amt'])

        bidList.sort(reverse=True)
        try:
            if len(bidList) >= self.pos:
                lastPrice = bidList[self.pos - 1]
            else:
                lastPrice = bidList[-1]
            logger('[MESSAGE] Total valid prices number is', len(bidList))
            return lastPrice
        except Exception:
            return False


def loopDelayRand():
    r = round(random.random() * LOOP_DELAY / 10, 2)
    return r


def resHandler(txt):
    try:
        j = json.loads(txt)
        return j
    except Exception:
        soup = BeautifulSoup(txt, 'html.parser')
        tempCheckRes = check503(soup)
        ldr = loopDelayRand()
        logger('[MESSAGE] Sleep ', ldr, 'seconds to try agian')
        time.sleep(ldr)
        return False


def requestUrl(ses, url, data, headers, proxies, func='post', changeIp=True):
    resStatus = True
    while resStatus == True:
        if changeIp == True:
            proxies = getProxy(USE_PROXIES, FIXED_PROXIES).getProxyFromWanbian()
        try:
            if func == 'post':
                response = ses.post(url, data=data, headers=headers, proxies=proxies, verify=False, timeout=TIMEOUT)
            else:
                if func == 'paraGet':
                    response = ses.get(url, params=data, headers=headers, proxies=proxies, verify=False, timeout=TIMEOUT)
                else:
                    if func == 'paraPost':
                        response = ses.post(url, params=data, headers=headers, proxies=proxies, verify=False, timeout=TIMEOUT)
                    else:
                        if func == 'get':
                            response = ses.get(url, headers=headers, proxies=proxies, verify=False, timeout=TIMEOUT)
            if response.status_code == 200:
                resStatus == False
                return (
                 response, proxies)
        except Exception:
            #说明登陆失败了
            logger('[FAIL] Requests failure. Change proxies and try again.')
            changeIp = True

#ordertime是现在的时间
def getOrdertimeWeb(ordertime, proxies, msMode):
    if msMode == 'm':
        url = 'https://m.48.cn//pai/GetTime?' + str(getTs())
    else:
        url = 'https://shop.48.cn//pai/GetTime?' + str(getTs())
    res = requests.get(url, headers=SHOP_HEADERS, proxies=proxies, verify=False, timeout=TIMEOUT)
    try:
        urltime = int(re.sub('[^0-9]', '', res.text))
        endtime = getTs(ordertime)
        difference_time = -300
        nowtime = getTs() + difference_time
        remain = endtime - nowtime
        logger('[SUCCESS] Get remain time successfully. Server time is', tsDate(urltime), '\nNowtime is', tsDate(nowtime), ',', remain / 1000, 'seconds remained')
        return remain
    except Exception:
        logger('[FAIL] Fail to get remain time')
        return False


def tsDate(t):
    t = round(t / 1000)
    local = time.localtime(t)
    dt = time.strftime('%Y-%m-%d %H:%M:%S', local)
    return dt

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

#默认在商城是购买票的，所以默认输入b
def getFunc():
    func = ''
    funcList = ['b', 'c', 'd']
    while func not in funcList:
        func = input('[INPUT-NEEDED] Specific a function (b: ticket/ c: bid item/ d: points goods), Leave empty to use default setting (b to order ticket) :')
        if func == '':
            func = 'b'
        func = str(func)

    return func


def saveCookies(path, ses):
    with open(path, 'a') as (f):
        json.dump(requests.utils.dict_from_cookiejar(ses.cookies), f)
        f.write('\n\n')


def loadCookies(path, ses, indexForCookies):
    with open(path, 'r') as (f):
        data = f.readlines()
        for i in range(len(data) - 1, -1, -1):
            if data[i] == '\n':
                data.pop(i)

        cookies = requests.utils.cookiejar_from_dict(json.loads(data[indexForCookies]))
        ses.cookies.update(cookies)


def check503(soup):
    lzs = soup.find('div', {'class': 'lz_s'})
    try:
        if lzs.text != None:
            logger('[FAIL] Server return 503 because requests too fast, set a higher delay to try again')
            return True
    except Exception:
        pass

    return False

#创建线程锁
def getLocks(sess):
    locks = []
    for inx in range(0, len(sess)):
        lock = thread.allocate_lock()
        lock.acquire()
        locks.append(lock)

    return locks


def main():
    #选择模拟购买的东西，默认是b，抢票
    func = getFunc()
    #读取配置文件
    gb = getConfigs(CONFIGS_PATH)
    #获取ip代理等配置
    USE_PROXIES, FIXED_PROXIES = gb.proxiesConfigs()
    #获取用户名，密码等
    users, pws = gb.loginConfigs()
    #msMode和TIMEOUT是两个变量，分别接收测试模式和超时时间的返回值
    msMode, TIMEOUT = gb.betaConfigs()
    #获取延迟
    auto, ticketDelay, proxyDelay, LOOP_DELAY = gb.timeConfigs()
    #proxies变量最终存储了从wanbian获取到的代理或者固定代理的信息。
    #如果use_proxies为1且，fixed_proxies为空则使用请求代理
    proxies = getProxy(USE_PROXIES, FIXED_PROXIES).getProxyFromWanbian()

    #获取当前时间
    ordertime = getTime()
    #通过倒计时函数进行一段随机长度的倒计时操作。倒计时长度在30到59秒之间
    countdown(ordertime, 30 + random.randint(0, 29))
    sess = []
    #users是用户列表
    for idx in range(0, len(users)):
        ses = requests.session()
        if os.path.exists(COOKIES_PATH) == True:
            loadCookies(COOKIES_PATH, ses, idx)
            logger('[MESSAGE] Cookies loaded, the total number of loaded cookies is', idx + 1)
        else:
            #idx是索引，开始一个一个登陆，并把每一个登陆会话加入到列表中
            #创建一个登陆对象
            a = login(users[idx], pws[idx], ses, proxies, msMode)
            #开始循环登陆
            a.loginInLoop()
        sess.append(ses)

    #sess是会话列表
    if func == 'b':
        locks = getLocks(sess)
        # 获取票的详细信息
        """
        showID：场次
        num：每个场次票的数量(一般是1)
        seattype：票的种类（2：vip座  3：普座 4：站座）
        walletPwd：钱包密码
        brandID:SNH、GNZ等等
        """
        showId, num, seattype, walletPwds, brandId = gb.ticketsConfigs()
    else:
        if func == 'c':
            bidId, priceLimit, pos, brandIdBid, increment, ocrAppcode = gb.bidConfigs()
        else:
            if func == 'd':
                locks = getLocks(sess)
                goodsId, goodsBrandId, goodNum, attrId, addressID, lgsId, province, city = gb.goodsConfigs()
    #auto 默认是1
    if auto == 0:
        #ordertime是当前时间
        countdown(ordertime, proxyDelay)
        time.sleep(ticketDelay)
    else:
        if auto == 1:
            remain = getOrdertimeWeb(ordertime, proxies, msMode)
            remain = remain / 1000
            if remain > 0 and remain < 600:
                logger('[MESSAGE] Wait', remain, 'seconds + ', ticketDelay, 'seconds')
                time.sleep(remain + ticketDelay)
            else:
                if remain < 0:
                    logger('[MESSAGE] No need to wait, because ordertime was passed')
        #之前已经登陆获取了会话列表sess
        for inx in range(len(sess) - 1, -1, -1):
            if func == 'b':
                #创建一个买票对象
                b = buyTicket(sess[inx], proxies, walletPwds[inx], showId[inx], num[inx], seattype[inx], brandId[inx], msMode)
                #开启一个线程进行抢票
                thread.start_new_thread(b.buyloop, (users[inx], locks[inx]))
            else:
                if func == 'c':
                    if len(sess) > 1:
                        logger('[MESSAGE] Bid helper is only available for the last account in list, which is', users[inx])
                    c = bid(sess[inx], proxies, bidId, priceLimit, pos, brandIdBid, increment, ocrAppcode, msMode)
                    c.bid()

        if func == 'b' or func == 'd':
            for i in range(len(locks)):
                while locks[i].locked():
                    pass

        logger('[MESSAGE] ALL DONE')
        time.sleep(30)


if __name__ == '__main__':
    main()
# okay decompiling snhopInList1.47.pyc




