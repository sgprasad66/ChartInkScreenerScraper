''' def test_finvasia_api():
    from NorenRestApiPy.NorenApi import  NorenApi
    import pyotp

    user        = ""
    pwd         = "*"
    vc          = ""
    app_key     = ""
    token       = ""

    class ShoonyaApiPy(NorenApi):
        def __init__(self):
            NorenApi.__init__(self, host="https://api.shoonya.com/NorenWClientTP/", websocket="wss://api.shoonya.com/NorenWSTP/")
            global api
            api = self

    try:
        api = ShoonyaApiPy()      
        #factor2 = str(input("Enter TOTP  here:"))
        two_fa=pyotp.TOTP(token).now()
        ret = api.login(userid=user, password=pwd, twoFA=two_fa, vendor_code=vc, api_secret=app_key, imei='00:FF:7E:4B:40:1E')
        #ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei='00:FF:7E:4B:40:1E')


        print(ret)

    except Exception as e:
        print(e)

    #print(ret)

if __name__ == '__main__':
    test_finvasia_api() '''
def downloadMasterFiles():
    import requests
    import zipfile
    import os
    root = 'https://api.shoonya.com/'
    masters = ['NSE_symbols.txt.zip', 'NFO_symbols.txt.zip', 'CDS_symbols.txt.zip', 'MCX_symbols.txt.zip', 'BSE_symbols.txt.zip'] 


    for zip_file in masters:    
        print(f'downloading {zip_file}')
        url = root + zip_file
        r = requests.get(url, allow_redirects=True)
        open(zip_file, 'wb').write(r.content)
        file_to_extract = zip_file.split()
    
        try:
            with zipfile.ZipFile(zip_file) as z:
                z.extractall()
                print("Extracted: ", zip_file)
        except:
            print("Invalid file")

        os.remove(zip_file)
        print(f'remove: {zip_file}')
import pandas as pd
from NorenRestApiPy.NorenApi import  NorenApi
#import logging
from datetime import datetime
import datetime as dt
from pytz import timezone
import pandas_ta as ta
#import broker 
import websocket
import os
import csv
import time
import math
import pyotp
from datetime import timedelta
pd.set_option('display.max_rows',None)

base=100
#symbol="NIFTY"
symbol="BANKNIFTY"
otm_points=100
bias_points=-100
sl_factor=1.25

global pe_tsym
global ce_tsym
global ce_strike
global pe_strike
global put_price
global call_price
global fno_scrips

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')
api = ShoonyaApiPy()

def init():
    
    user        = ""
    pwd         = ""
    vc          = ""
    app_key     = ""
    token       = ""
    global fno_scrips
#app_key     = # broker.get_appkey().rstrip("\n") ##your app key
    time.sleep(2)
    while True:
        try:
            factor2  = pyotp.TOTP(token).now()
            ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei='00:FF:7E:4B:40:1E')
            if ret['stat']=='Ok' : 
                print ('login successful')
                break
        except Exception:
            print('could not login, retrying')
            time.sleep(2)
            continue  

'''     fno_scrips = pd.read_csv('NFO_symbols.txt',delimiter=',')
    #print(fno_scrips)
    fno_scrips['Expiry'] = pd.to_datetime(fno_scrips['Expiry'])
    fno_scrips['StrikePrice'] = fno_scrips['StrikePrice'].astype(float)
    fno_scrips.sort_values('Expiry',inplace=True)
    fno_scrips.reset_index(drop=True, inplace=True)
    print(fno_scrips.head(5)) '''



def get_atm_strike():
    global fno_scrips
    global atm_strike
    fut_token=str(fno_scrips[(fno_scrips['Instrument']=='FUTIDX') & (fno_scrips['Symbol']==symbol)].sort_values('Expiry').iloc[0]['Token']) 
    print(fut_token)
    #fut_token = '35014'
    fut=float(api.get_quotes(exchange='NFO', token=fut_token)['lp'])
          
    atm_strike=round(fut/base)*base
    print("Current ATM strike for NIFTY-->")
    print(atm_strike)
    return atm_strike

def get_option_strikes() :
    atm_strike=get_atm_strike() 
    ce_strike=atm_strike+otm_points+bias_points
    pe_strike=atm_strike-otm_points+bias_points
    return(ce_strike,pe_strike)

#following func. returns all the scrip details , extract anything using key
def get_symbol(symbol,strike_price,optiontype):
    trading_symbol=fno_scrips[(fno_scrips['Symbol']==symbol) & (fno_scrips['OptionType']==optiontype) & (fno_scrips['StrikePrice']==strike_price)].iloc[0]
    return(trading_symbol)

def get_token(symbol,strike_price,optiontype):
    trading_symbol_token=fno_scrips[(fno_scrips['Symbol']==symbol) & (fno_scrips['OptionType']==optiontype) & (fno_scrips['StrikePrice']==strike_price)].iloc[0] 
    return(trading_symbol_token)

def place_strangle(ce_trading_symbol,pe_trading_symbol) :
    
    ##placing orders*************************************************
    ce_order=api.place_order(buy_or_sell='S', product_type='M',
                        exchange='NFO', tradingsymbol=ce_trading_symbol, 
                        quantity=15, discloseqty=0,price_type='MKT', price=0, trigger_price=None,
                        retention='DAY', remarks='ce_order_001')
    pe_order=api.place_order(buy_or_sell='S', product_type='M',
                        exchange='NFO', tradingsymbol=pe_trading_symbol, 
                        quantity=15, discloseqty=0,price_type='MKT', price=0, trigger_price=None,
                        retention='DAY', remarks='pe_order_001')
    ce_order_id=ce_order['norenordno']
    pe_order_id=pe_order['norenordno']
    
    return(ce_order_id,pe_order_id)
    #return('23072701144878','23072701144884')

def place_stop(tysm,sl_prc) :
    #define_trigg
    sl_trigg = sl_prc - 0.1
    sl_order=api.place_order(buy_or_sell='B', product_type='M',
                        exchange='NFO', tradingsymbol=tysm, 
                        quantity=15, discloseqty=0,price_type='SL-LMT', price=sl_prc, trigger_price=sl_trigg,
                        retention='DAY', remarks='sl_001')
    sl_order_id=sl_order['norenordno']
    return(sl_order_id)

    
def order_history(orderid,req): 
        while True: 
            json_data=api.single_order_history(orderid)
            if json_data!=None:
                break

        for id in json_data:
            if  not (id['status'] == 'REJECTED'):
                value_return=id[req]
                break

        return value_return

def trail_sl(ce_sl_order_id,pe_sl_order_id):
    global pe_tsym
    global ce_tsym
    global put_price
    global call_price

    while True : 
        time.sleep(1)
        call_sl_status= order_history(ce_sl_order_id,'status')
        put_sl_status=order_history(pe_sl_order_id,'status')

        if call_sl_status=='COMPLETE':
            put_sl_to_cost = api.modify_order(exchange='NFO', tradingsymbol=pe_tsym, orderno=pe_sl_order_id,
                                 newquantity=15, newprice_type='SL-LMT', newprice=put_price, newtrigger_price=put_price-0.1)
            naked_leg_sym=pe_tsym
            break  

        if put_sl_status=='COMPLETE':
            call_sl_to_cost= api.modify_order(exchange='NFO', tradingsymbol=ce_tsym, orderno=ce_sl_order_id,
                                 newquantity=15, newprice_type='SL-LMT', newprice=call_price, newtrigger_price=call_price-0.1)
            naked_leg_sym=ce_tsym
            break
    return(naked_leg_sym)

def options_straddle_strangle():
    global pe_tsym
    global ce_tsym
    global put_price
    global call_price
    global atm_strike

    strikes = get_option_strikes()
    print(strikes)
    ce_strike=strikes[0]
    pe_strike=strikes[1]
    ##get symbols of PE & CE *****************************************
    ce_tsym=get_symbol(symbol,ce_strike,"CE")['TradingSymbol'] 
    pe_tsym=get_symbol(symbol,pe_strike,"PE")['TradingSymbol'] 

    oc = api.get_option_chain('NFO', ce_tsym, atm_strike, 4)
    df1 = pd.DataFrame(oc['values'])
    print(df1)
    dict_data = {}

# Iterate through the DataFrame rows
    for index, row in df1.iterrows():
        key = (row['strprc'], row['optt'])  # Use a tuple of 'Name' and 'City' as the key
        value = {str(row['token'])+' '+str(row['tsym'])}      # Create a dictionary with 'Age' as the value
        dict_data[key] = value           # Add key-value pair to the dictionary

        #dict_data = df1.to_dict(orient='dict')

    print("Dictionary with multiple columns as keys:")
    print(dict_data)

    strangle_orders=place_strangle(ce_tsym,pe_tsym)
    call_price=float(order_history(strangle_orders[0],'avgprc'))
    put_price=float(order_history(strangle_orders[1],'avgprc'))
    #define sl price


feed_opened = False
feedJson = {}
def event_handler_order_update(order):
    print(f"order feed {order}")

def event_handler_quote_update():
    pass

def balanceDelta_ce():
    pass


def balanceDelta_pe():
    pass

def open_callback():
    global socket_opened
    socket_opened = True
    print('app is connected')
    #api.subscribe_orders()
    #api.subscribe('NFO|35014')
    #api.subscribe('MCX|253460','MCX|259212','MCX|259211')
    api.subscribe('MCX|425428','MCX|425442')
    print('Subscribed to 425428 and 425442')
    #api.subscribe(['NSE|22', 'BSE|522032'])


if __name__ == '__main__':
    #downloadMasterFiles()
    init()
    #options_straddle_strangle()
    #ret = api.start_websocket(order_update_callback=event_handler_order_update, subscribe_callback=event_handler_quote_update, socket_open_callback=open_callback)
    api.start_websocket(order_update_callback=event_handler_order_update, subscribe_callback=event_handler_quote_update, socket_open_callback=open_callback)            

    print('ret')
    while True:
        balanceDelta_ce()
        balanceDelta_pe()
        #time.sleep(30) 
        

''' def test_finvasia_api():
    from NorenRestApiPy.NorenApi import  NorenApi
    import pyotp

    user        = "FA136660"
    pwd         = "SpiritFav66*"
    vc          = "FA136660_U"
    app_key     = "f3fc8d474408bb1095ee5939ab91d1ca"
    token       = "G343QP74S42M3C33EV3F4K5363B7V6M4"

    class ShoonyaApiPy(NorenApi):
        def __init__(self):
            NorenApi.__init__(self, host="https://api.shoonya.com/NorenWClientTP/", websocket="wss://api.shoonya.com/NorenWSTP/")
            global api
            api = self

    try:
        api = ShoonyaApiPy()      
        #factor2 = str(input("Enter TOTP  here:"))
        two_fa=pyotp.TOTP(token).now()
        ret = api.login(userid=user, password=pwd, twoFA=two_fa, vendor_code=vc, api_secret=app_key, imei='00:FF:7E:4B:40:1E')
        #ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei='00:FF:7E:4B:40:1E')


        print(ret)

    except Exception as e:
        print(e)

    #print(ret)

if __name__ == '__main__':
    test_finvasia_api() '''
def downloadMasterFiles():
    import requests
    import zipfile
    import os
    root = 'https://api.shoonya.com/'
    masters = ['NSE_symbols.txt.zip', 'NFO_symbols.txt.zip', 'CDS_symbols.txt.zip', 'MCX_symbols.txt.zip', 'BSE_symbols.txt.zip'] 


    for zip_file in masters:    
        print(f'downloading {zip_file}')
        url = root + zip_file
        r = requests.get(url, allow_redirects=True)
        open(zip_file, 'wb').write(r.content)
        file_to_extract = zip_file.split()
    
        try:
            with zipfile.ZipFile(zip_file) as z:
                z.extractall()
                print("Extracted: ", zip_file)
        except:
            print("Invalid file")

        os.remove(zip_file)
        print(f'remove: {zip_file}')
import pandas as pd
from NorenRestApiPy.NorenApi import  NorenApi
#import logging
from datetime import datetime
import datetime as dt
from pytz import timezone
import pandas_ta as ta
#import broker 
import websocket
import os
import csv
import time
import math
import pyotp
from datetime import timedelta
pd.set_option('display.max_rows',None)

base=100
#symbol="NIFTY"
symbol="BANKNIFTY"
otm_points=100
bias_points=-100
sl_factor=1.25

global pe_tsym
global ce_tsym
global ce_strike
global pe_strike
global put_price
global call_price
global fno_scrips

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')
api = ShoonyaApiPy()

def init():
    
    user        = "FA136660"
    pwd         = "SpiritWas12#"
    vc          = "FA136660_U"
    app_key     = "f3fc8d474408bb1095ee5939ab91d1ca"
    token       = "G343QP74S42M3C33EV3F4K5363B7V6M4"
    global fno_scrips
#app_key     = # broker.get_appkey().rstrip("\n") ##your app key
    time.sleep(2)
    while True:
        try:
            factor2  = pyotp.TOTP(token).now()
            ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei='00:FF:7E:4B:40:1E')
            if ret['stat']=='Ok' : 
                print ('login successful')
                break
        except Exception:
            print('could not login, retrying')
            time.sleep(2)
            continue  

'''     fno_scrips = pd.read_csv('NFO_symbols.txt',delimiter=',')
    #print(fno_scrips)
    fno_scrips['Expiry'] = pd.to_datetime(fno_scrips['Expiry'])
    fno_scrips['StrikePrice'] = fno_scrips['StrikePrice'].astype(float)
    fno_scrips.sort_values('Expiry',inplace=True)
    fno_scrips.reset_index(drop=True, inplace=True)
    print(fno_scrips.head(5)) '''



def get_atm_strike():
    global fno_scrips
    global atm_strike
    fut_token=str(fno_scrips[(fno_scrips['Instrument']=='FUTIDX') & (fno_scrips['Symbol']==symbol)].sort_values('Expiry').iloc[0]['Token']) 
    print(fut_token)
    #fut_token = '35014'
    fut=float(api.get_quotes(exchange='NFO', token=fut_token)['lp'])
          
    atm_strike=round(fut/base)*base
    print("Current ATM strike for NIFTY-->")
    print(atm_strike)
    return atm_strike

def get_option_strikes() :
    atm_strike=get_atm_strike() 
    ce_strike=atm_strike+otm_points+bias_points
    pe_strike=atm_strike-otm_points+bias_points
    return(ce_strike,pe_strike)

#following func. returns all the scrip details , extract anything using key
def get_symbol(symbol,strike_price,optiontype):
    trading_symbol=fno_scrips[(fno_scrips['Symbol']==symbol) & (fno_scrips['OptionType']==optiontype) & (fno_scrips['StrikePrice']==strike_price)].iloc[0]
    return(trading_symbol)

def get_token(symbol,strike_price,optiontype):
    trading_symbol_token=fno_scrips[(fno_scrips['Symbol']==symbol) & (fno_scrips['OptionType']==optiontype) & (fno_scrips['StrikePrice']==strike_price)].iloc[0] 
    return(trading_symbol_token)

def place_strangle(ce_trading_symbol,pe_trading_symbol) :
    
    ##placing orders*************************************************
    ce_order=api.place_order(buy_or_sell='S', product_type='M',
                        exchange='NFO', tradingsymbol=ce_trading_symbol, 
                        quantity=15, discloseqty=0,price_type='MKT', price=0, trigger_price=None,
                        retention='DAY', remarks='ce_order_001')
    pe_order=api.place_order(buy_or_sell='S', product_type='M',
                        exchange='NFO', tradingsymbol=pe_trading_symbol, 
                        quantity=15, discloseqty=0,price_type='MKT', price=0, trigger_price=None,
                        retention='DAY', remarks='pe_order_001')
    ce_order_id=ce_order['norenordno']
    pe_order_id=pe_order['norenordno']
    
    return(ce_order_id,pe_order_id)
    #return('23072701144878','23072701144884')

def place_stop(tysm,sl_prc) :
    #define_trigg
    sl_trigg = sl_prc - 0.1
    sl_order=api.place_order(buy_or_sell='B', product_type='M',
                        exchange='NFO', tradingsymbol=tysm, 
                        quantity=15, discloseqty=0,price_type='SL-LMT', price=sl_prc, trigger_price=sl_trigg,
                        retention='DAY', remarks='sl_001')
    sl_order_id=sl_order['norenordno']
    return(sl_order_id)

    
def order_history(orderid,req): 
        while True: 
            json_data=api.single_order_history(orderid)
            if json_data!=None:
                break

        for id in json_data:
            if  not (id['status'] == 'REJECTED'):
                value_return=id[req]
                break

        return value_return

def trail_sl(ce_sl_order_id,pe_sl_order_id):
    global pe_tsym
    global ce_tsym
    global put_price
    global call_price

    while True : 
        time.sleep(1)
        call_sl_status= order_history(ce_sl_order_id,'status')
        put_sl_status=order_history(pe_sl_order_id,'status')

        if call_sl_status=='COMPLETE':
            put_sl_to_cost = api.modify_order(exchange='NFO', tradingsymbol=pe_tsym, orderno=pe_sl_order_id,
                                 newquantity=15, newprice_type='SL-LMT', newprice=put_price, newtrigger_price=put_price-0.1)
            naked_leg_sym=pe_tsym
            break  

        if put_sl_status=='COMPLETE':
            call_sl_to_cost= api.modify_order(exchange='NFO', tradingsymbol=ce_tsym, orderno=ce_sl_order_id,
                                 newquantity=15, newprice_type='SL-LMT', newprice=call_price, newtrigger_price=call_price-0.1)
            naked_leg_sym=ce_tsym
            break
    return(naked_leg_sym)

def options_straddle_strangle():
    global pe_tsym
    global ce_tsym
    global put_price
    global call_price
    global atm_strike

    strikes = get_option_strikes()
    print(strikes)
    ce_strike=strikes[0]
    pe_strike=strikes[1]
    ##get symbols of PE & CE *****************************************
    ce_tsym=get_symbol(symbol,ce_strike,"CE")['TradingSymbol'] 
    pe_tsym=get_symbol(symbol,pe_strike,"PE")['TradingSymbol'] 

    oc = api.get_option_chain('NFO', ce_tsym, atm_strike, 4)
    df1 = pd.DataFrame(oc['values'])
    print(df1)
    dict_data = {}

# Iterate through the DataFrame rows
    for index, row in df1.iterrows():
        key = (row['strprc'], row['optt'])  # Use a tuple of 'Name' and 'City' as the key
        value = {str(row['token'])+' '+str(row['tsym'])}      # Create a dictionary with 'Age' as the value
        dict_data[key] = value           # Add key-value pair to the dictionary

        #dict_data = df1.to_dict(orient='dict')

    print("Dictionary with multiple columns as keys:")
    print(dict_data)

    strangle_orders=place_strangle(ce_tsym,pe_tsym)
    call_price=float(order_history(strangle_orders[0],'avgprc'))
    put_price=float(order_history(strangle_orders[1],'avgprc'))
    #define sl price


feed_opened = False
feedJson = {}
def event_handler_order_update(order):
    print(f"order feed {order}")

def event_handler_quote_update():
    pass

def balanceDelta_ce():
    pass


def balanceDelta_pe():
    pass

def open_callback():
    global socket_opened
    socket_opened = True
    print('app is connected')
    #api.subscribe_orders()
    #api.subscribe('NFO|35014')
    #api.subscribe('MCX|253460','MCX|259212','MCX|259211')
    api.subscribe('MCX|425428','MCX|425442')
    print('Subscribed to 425428 and 425442')
    #api.subscribe(['NSE|22', 'BSE|522032'])


if __name__ == '__main__':
    #downloadMasterFiles()
    init()
    #options_straddle_strangle()
    #ret = api.start_websocket(order_update_callback=event_handler_order_update, subscribe_callback=event_handler_quote_update, socket_open_callback=open_callback)
    api.start_websocket(order_update_callback=event_handler_order_update, subscribe_callback=event_handler_quote_update, socket_open_callback=open_callback)            

    print('ret')
    while True:
        balanceDelta_ce()
        balanceDelta_pe()
        #time.sleep(30) 
        