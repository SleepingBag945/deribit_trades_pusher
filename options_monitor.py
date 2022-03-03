from deri_api import RestClient
import requests
import time, datetime
from PIL import Image,ImageFont,ImageDraw
import os
trade_id_btc = 0
trade_id_eth = 0


def gettrades_btc():
    global trade_id_btc
    sum_trades_options = []
    sum_trades_futures = []
    has_more = True
    while has_more:
        result = None
        try:
            result = dr.getlasttradesbycurrency('BTC',count = 1000,start_id = trade_id_btc)
        except requests.exceptions.ConnectionError:
            print("requests.exceptions.ConnectionError. Thread hibernates for 15 seconds")
            time.sleep(15)

        trades = result['trades']
        if len(trades) == 0:
            return [[],[]]
        has_more = result['has_more']
        for trade in trades:
            key = trade['instrument_name'][-2:]
            if key == "-P" or key == "-C":
                sum_trades_options.append(trade)
            else:
                sum_trades_futures.append(trade)
        
        trade_id_btc = int(trades[-1]['trade_id']) + 1

    return [sum_trades_options,sum_trades_futures]

def gettrades_eth():
    global trade_id_eth
    sum_trades_options = []
    sum_trades_futures = []
    has_more = True
    while has_more:
        result = None
        try:
            result = dr.getlasttradesbycurrency('ETH',count = 1000,start_id = trade_id_eth)
        except requests.exceptions.ConnectionError:
            print("requests.exceptions.ConnectionError. Thread hibernates for 15 seconds")
            time.sleep(15)
            
        trades = result['trades']
        if len(trades) == 0:
            return [[],[]]
        has_more = result['has_more']
        for trade in trades:
            key = trade['instrument_name'][-2:]
            if key == "-P" or key == "-C":
                sum_trades_options.append(trade)
            else:
                sum_trades_futures.append(trade) 
        
        trade_id_eth = "ETH-{}".format(int(trades[-1]['trade_id'].replace("ETH-","")) + 1)
    return [sum_trades_options,sum_trades_futures]

def generate_pic(option):
    info = dr.getoptionsinfobyname(option['instrument_name'])
    font_currency = ImageFont.truetype(u'MiSans-Medium.ttf',40)
    font_type = ImageFont.truetype(u'MiSans-Medium.ttf',30)
    font_20 = ImageFont.truetype(u'MiSans-Medium.ttf',20)
    font_s = ImageFont.truetype(u'MiSans-Medium.ttf',15)
    picname = '{}.png'.format(option['direction'])
    im = Image.open(picname)
    draw = ImageDraw.Draw(im)

    #标的名称
    draw.text((55,19),info['currency'],font = font_currency)

    #合约类别 Call or Put
    type_color = "#e05b5a"
    if info['type'] == "Call":
        type_color = "#2f9675"
    draw.text((198,22),info['type'].upper(),font = font_type,fill = type_color)

    #过期日 (天数)
    left_color = "#ffffff"
    if float(info['leftdays']) <= 7:
        left_color = "#FF1493"
    draw.text((22,90),'过期日 (天数)',font = font_s,fill = "#808080")#行权日
    draw.text((22,110),info['exercise_date']+" ( {} ) ".format(info['leftdays']),font = font_20,fill = left_color)#行权日

    #行权价
    draw.text((240,90),'行权价',font = font_s,fill = "#808080")
    draw.text((240,110),str(info['exercise_price']),font = font_20,fill = "#ffffff")

    #币价
    draw.text((340,90),'标的价格',font = font_s,fill = "#808080")
    draw.text((340,110),str(option['index_price']),font = font_20,fill = "#ffffff")

    #成交时间
    draw.text((470,90),'时间',font = font_s,fill = "#808080")
    draw.text((470,114),dr._D(option['timestamp']),font = font_s,fill = "#ffffff")

    #合约价格
    draw.text((380,20),'合约价格',font = font_s,fill = "#808080")
    draw.text((455,20),'{} {} = {:.2f} USD'.format(option['price'],info['currency'],float(option['price']) * float(option['index_price'])),font = font_s,fill = "#ffffff")

    #成交数量
    draw.text((380,38),'成交数量',font = font_s,fill = "#808080")
    draw.text((455,38),'{}张 = {:.2f} USD'.format(option['amount'],float(option['amount']) * float(option['price']) * float(option['index_price'])),font = font_s,fill = "#ffffff")

    #成交数量
    draw.text((380,56),'隐含波动率(IV)',font = font_s,fill = "#808080")
    draw.text((500,56),'{:.2f}%'.format(option['iv']),font = font_s,fill = "#ffffff")
    im.save("/usr/local/nginx/html/" + option['trade_id'] + ".png")   

    
    
def generate_pic_future(future):
    print(future['instrument_name'])
    info = dr.getoptionsinfobyname_future(future['instrument_name'])
    print(info)
    font_currency = ImageFont.truetype(u'MiSans-Medium.ttf',40)
    font_type = ImageFont.truetype(u'MiSans-Medium.ttf',30)
    font_20 = ImageFont.truetype(u'MiSans-Medium.ttf',20)
    font_s = ImageFont.truetype(u'MiSans-Medium.ttf',15)
    picname = '{}.png'.format(future['direction'])
    im = Image.open(picname)
    draw = ImageDraw.Draw(im)

    #标的名称
    draw.text((55,19),info['currency'],font = font_currency)

    #合约类别 永续 or 交割
    type_color = "#00BFFF"
    if info['type'] == 'PERP':
        draw.text((198,22),info['type'].upper(),font = font_type,fill = type_color)
    else:
        draw.text((195,30),info['type'].upper(),font = font_20,fill = type_color)

    #过期日 (天数)
    left_color = "#ffffff"
    if info['leftdays'] != "∞" and float(info['leftdays']) <= 7:
        left_color = "#FF1493"
    draw.text((22,90),'过期日 (天数)',font = font_s,fill = "#808080")#行权日
    draw.text((22,110),info['exercise_date']+" ( {} ) ".format(info['leftdays']),font = font_20,fill = left_color)#行权日

    #行权价
    draw.text((240,90),'成交价格',font = font_s,fill = "#808080")
    draw.text((240,110),str(future['price']),font = font_20,fill = "#ffffff")

    #币价
    draw.text((340,90),'标记价格',font = font_s,fill = "#808080")
    draw.text((340,110),str(future['index_price']),font = font_20,fill = "#ffffff")

    #成交时间
    draw.text((470,90),'时间',font = font_s,fill = "#808080")
    draw.text((470,114),dr._D(future['timestamp']),font = font_s,fill = "#ffffff")

    #成交数量
    draw.text((380,38),'成交数量',font = font_s,fill = "#808080")
    draw.text((455,38),'{} USD = {:.2f} {}'.format(future['amount'],float(future['amount']) / future['price'],info['currency']),font = font_s,fill = "#ffffff")

    im.save("/usr/local/nginx/html/" + future['trade_id'] + ".png")  
    
    
def gettext(big_trades_list):
    text = ""
    for trade_id in big_trades_list:
        text += "> ![screenshot](http://202.182.124.128:29999/{}.png)\n".format(trade_id)
    return text[:-1]
    
def scan():
    big_trades_list = []
    btc_sum_vol = 0
    btc = gettrades_btc()
    for option in btc[0]:
        if option['amount'] < 30:#过滤出30BTC以上期权订单
            continue
        big_trades_list.append(option['trade_id'])
        btc_sum_vol += float(option['amount'])
        generate_pic(option)
    for future in btc[1]:
        if float(future['amount']) / float(future['price']) < 30:#过滤出30BTC以上期货订单
            continue
        generate_pic_future(future)
        big_trades_list.append(future['trade_id'])
        
        
    eth_sum_vol = 0    
    eth = gettrades_eth()
    for option in eth[0]:
        if option['amount'] < 500:#过滤出500ETH以上期权订单
            continue
        big_trades_list.append(option['trade_id'])
        eth_sum_vol += float(option['amount'])
        generate_pic(option)
    for future in eth[1]:
        if float(future['amount']) / float(future['price']) < 500:#过滤出500ETH以上期货订单
            continue
        generate_pic_future(future)
        big_trades_list.append(future['trade_id'])

    headers = {"Content-Type":"application/json"}
    
    
    # 在这里更改access_token
    url = 'https://oapi.dingtalk.com/robot/send?access_token=Your_Token'
    
    msg = {
     "msgtype": "markdown",
     "markdown": {
         "title":"[Alert] ₿*{} E*{}".format(btc_sum_vol,eth_sum_vol),
         "text": gettext(big_trades_list)
     }
    }
    times = 0
    while True:
        try:
            r = requests.post(url,json = msg,headers=headers)
        except requests.exceptions.ConnectionError:
            print("requests.exceptions.ConnectionError. Thread hibernates for 15 seconds")
            time.sleep(15)
        times += 1
        if r.status_code == 200 or times > 5:
            break


if __name__ == '__main__':
    #在scan函数内更改你的钉钉自定义机器人access_token

    
    #在29999端口搭建HTTP服务器。这里使用的是nginx   根目录为：/usr/local/nginx/html/
    
    
    #放通29999端口
    #firewall-cmd --zone=public --add-port=29999/tcp --permanent
    #firewall-cmd --reload
    
    #运行jio本
    #python3 options_monitor.py >> /root/optionslog.log 2>&1 &
    
    dr = RestClient(useproxy = False)
    trade_id_btc = int(dr.getlasttradesbycurrency(currency = "BTC",count = 1)['trades'][0]['trade_id'])
    if trade_id_btc <= 0:
        raise Exception("Failed: Can't get the tradeid of btc")
    trade_id_eth = dr.getlasttradesbycurrency(currency = "ETH",count = 1)['trades'][0]['trade_id']
    if int(trade_id_eth.replace("ETH-","")) <= 0:
        raise Exception("Failed: Can't get the tradeid of eth")
    print(f"The monitoring system has been started. BTC:{trade_id_btc} ETH:{trade_id_eth}")
    
    #定期清理累计的图片
    timess = 0
    while True:
        scan()
        time.sleep(20)
        timess += 1
        if timess > 30240:
            for files in os.listdir('/usr/local/nginx/html/'):
                if files.endswith(".png"):
                    os.remove(os.path.join('pic',files))
            timess = 0
        