import time, hashlib, requests, base64, sys, hmac
from collections import OrderedDict
import datetime


class RestClient(object):
    def __init__(self, url = "https://www.deribit.com",useproxy = False):
        self.useproxy = useproxy
        self.session = requests.Session()
        self.url = url
        
    def request(self, action, data):
        response = None
        times = 0
        while True:
            if self.useproxy:
            #V2ray HTTP Proxy 用于解决国内Deribit访问速度偏慢的问题。
                response = self.session.get(self.url + action, params=data, proxies = {'http':'http://127.0.0.1:10809','https':'http://127.0.0.1:10809'})
            else:
                response = self.session.get(self.url + action, params=data)
            times += 1
            if response.status_code == 200 or time > 5:
                break
        
        if response.status_code != 200:
            print(action,data)
            raise Exception("Wrong response code: {0}".format(response.status_code))

        json = response.json()

        if "error" in json:
            raise Exception("Failed: " + json["error"])

        if "result" in json:
            return json["result"]
        elif "message" in json:
            return json["message"]
        else:
            return "Ok"

    def getindex(self, currency):
        return self.request("/api/v2/public/get_index", {'currency': currency})
    
    def getlasttradesbycurrency(self,currency,count,start_id = 0):
        if int(str(start_id).replace("ETH-","")) < 0:
            raise Exception("Failed: startid < 0")
        if int(str(start_id).replace("ETH-","")) == 0:
            return self.request("/api/v2/public/get_last_trades_by_currency", {'currency': currency,'count':count})
        else:
            return self.request("/api/v2/public/get_last_trades_by_currency", {'currency': currency,'count':count,'start_id':start_id})

    def getlasttradesbycurrency_kind(self,currency,kind,count,start_id = 0):
        if int(str(start_id).replace("ETH-","")) < 0:
            raise Exception("Failed: startid < 0")
        if int(str(start_id).replace("ETH-","")) == 0:
            return self.request("/api/v2/public/get_last_trades_by_currency", {'currency': currency,'count':count,'kind':kind})
        else:
            return self.request("/api/v2/public/get_last_trades_by_currency", {'currency': currency,'count':count,'kind':kind,'start_id':start_id})
    
    def getoptionsinfobyname(self,name):
        sp = name.split('-')
        res = {}
        if len(sp) != 4:
            return res
        
        res['currency'] = sp[0]
        timeArray = time.strptime(sp[1], "%d%b%y")
        res['exercise_date'] = time.strftime("%Y.%m.%d" , timeArray)
        res['exercise_date_ts'] = int(time.mktime(timeArray) * 1000) + 28800000
        res['leftdays'] = "{:.1f}".format((res['exercise_date_ts'] - int(time.time() * 1000)) / 86400000)
        res['exercise_price'] = int(sp[2])
        if sp[3] == "P":
            res['type'] = "Put"
        elif sp[3] == "C": 
            res['type'] = "Call"
        return res
    
    def getoptionsinfobyname_future(self,name):
        sp = name.split('-')
        res = {}
        if len(sp) != 2:
            return res
        
        res['currency'] = sp[0]
        if sp[1] != "PERPETUAL":
            timeArray = time.strptime(sp[1], "%d%b%y")
            res['exercise_date'] = time.strftime("%Y.%m.%d" , timeArray)
            res['exercise_date_ts'] = int(time.mktime(timeArray) * 1000) + 28800000
            res['leftdays'] = "{:.1f}".format((res['exercise_date_ts'] - int(time.time() * 1000)) / 86400000)
            res['type'] = sp[1]
        else:
            res['exercise_date'] = '∞'
            res['exercise_date_ts'] = '∞'
            res['leftdays'] = '∞'
            res['type'] = "PERP"
         
        return res
    
    def _D(self,times):
        dateArray = datetime.datetime.fromtimestamp(int(times) / 1000)
        return dateArray.strftime("%Y.%m.%d %H:%M:%S") + '.' + str(times % 1000)