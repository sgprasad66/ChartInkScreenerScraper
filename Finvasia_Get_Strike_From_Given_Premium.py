from time import sleep
import time
import datetime
from datetime import datetime,timedelta
import pandas as pd
from ChartInk_Scaper_FileWatcher_Processor import stockitem
import helper
import pymongo
import certifi
import datetime
from NorenRestApiPy.NorenApi import  NorenApi
from datetime import datetime
import datetime as dt
import time
import pyotp

pd.set_option('display.max_rows',None)


config = helper.read_config()
mongodbclient = config['MongoDBSettings']['mongodbclient']
databasename = config['MongoDBSettings']['databasename']
collectionname = config['MongoDBSettings']['collectionname']
deletecollectionname=config['MongoDBSettings']['deletecollectionname']
feed_opened = False
socket_opened = False
feedJson={}
client = pymongo.MongoClient(mongodbclient,tlsCAFile=certifi.where())

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')
api = ShoonyaApiPy()

def init():
    
    user        = "Username"
    pwd         = "Password"
    vc          = "%%%%%%%%"
    app_key     = "%%%%%%%%%%%%%%%%%"
    token       = "%%%%%%%%%%%%"
    global fno_scrips
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

def event_handler_feed_update(tick_data):
    UPDATE = False
    if 'tk' in tick_data:
        token = tick_data['tk']
        timest = datetime.fromtimestamp(int(tick_data['ft'])).isoformat()
        feed_data = {'tt': timest}
        if 'lp' in tick_data:
            feed_data['ltp'] = float(tick_data['lp'])
        if 'ts' in tick_data:
            feed_data['Tsym'] = str(tick_data['ts'])
        if 'oi' in tick_data:
            feed_data['openi'] = float(tick_data['oi'])
        if 'poi' in tick_data:
            feed_data['pdopeni'] = str(tick_data['poi'])
        if 'v' in tick_data:
            feed_data['Volume'] = str(tick_data['v'])     
        if feed_data:
            UPDATE = True
            if token not in feedJson:
                feedJson[token] = {}
            feedJson[token].update(feed_data)
        if UPDATE:
             pass#print(f'Token:{token} Feed:{feedJson[token]}')

def event_handler_order_update(order_update):
    pass#print(f"order feed {order_update}") 

def open_callback():
    global feed_opened
    feed_opened = True
    print("Websocket opened")

def setupWebSocket():
    global feed_opened
    print("waiting for socket opening")
    api.start_websocket(order_update_callback=event_handler_order_update,
                         subscribe_callback=event_handler_feed_update, 
                         socket_open_callback=open_callback)    
    while(feed_opened==False):        
        pass

init()
setupWebSocket()


def get_token_from_symbol(exchange,symbol):
    symb_one_strike=0
    symb_two_strike=0
    strike_diff=0
    token=0

    ret = api.searchscrip(exchange=exchange, searchtext=symbol)

    if ret != None:
        symbols = ret['values']
        for symbol_index in symbols:
            token = symbol_index['token']

    ret = api.searchscrip(exchange='NFO', searchtext=symbol)
    if ret != None:
        symbols = ret['values']
        for symbol_idx in symbols:
            if symbol_idx['instname'] == 'OPTSTK' or symbol_idx['instname'] == 'OPTIDX':
                if symbol_idx['dname'].split(' ')[3] == 'CE':
                    if symb_one_strike == 0:
                        symb_one_strike =int(symbol_idx['dname'].split(' ')[2])
                        #continue
                    else:
                        symb_two_strike = int(symbol_idx['dname'].split(' ')[2])
                        break
    strike_diff = abs(symb_one_strike-symb_two_strike)
    return token,strike_diff

    #print('{0} token is {1}'.format(symbol['tsym'], symbol['token']))

def options_Buy_ATM_Calls_Sell_DeepITM_Call(symbol,option_type):
    global pe_tsym
    global ce_tsym
    global put_price
    global call_price
    global atm_strike
    global atm_expiry
    global atm_token

    exch = symbol.split(':')[0]
    sym_to_search = symbol.split(':')[1]

    tok,strike_diff = get_token_from_symbol(exch,sym_to_search)
    atm_expiry = get_expiry_dates('NFO', sym_to_search)[1]
    #expiry_date = get_expiry_dates('MCX', 'CRUDEOILM')[0]
    print(atm_expiry)
    ''' if symbol == 'Nifty':
        ret = api.get_quotes(exchange='NSE', token='26000') #for NIFTY token is 26000
    else:
        ret = api.get_quotes(exchange='NSE', token='26009') '''

    ret = api.get_quotes(exchange='NSE', token=tok)
    ltp = ret.get("lp")
    atm_ltp = float(ltp)
    ltp_str = str(float(ltp))
    sym = ret.get("symname")
    TYPE = option_type
    ''' if symbol == 'Nifty':
        Strike = int(round(float(ltp)/50,0)*50)
    else:
        Strike = int(round(float(ltp)/100,0)*100) '''
    
    #Strike = int(round(float(ltp)/100,0)*100)
    Strike = int(round(float(ltp)/float(strike_diff),0)*float(strike_diff))
    print(Strike)
    For_token = sym+atm_expiry+TYPE+str(Strike)
    ret_val = api.searchscrip('NFO',For_token)

    if ret_val != None:
        symbols = ret_val['values']
        for symbol_loop in symbols:
        #print('{0} token is {1}'.format(symbol['tsym'], symbol['token']))
            atm_token = symbol_loop['token']
            atm_token_lotsize = int(symbol_loop['ls'])

    ret_quote = api.get_quotes(exchange='NFO', token=atm_token)
    ltp_price = ret_quote["lp"]
    optionchain = api.get_option_chain('NFO', For_token , Strike, 10)
    optionchainsym = (optionchain['values'])
    for Symbol in optionchainsym:
        (Symbol['token']) 
        
    token= [Symbol['token'] for Symbol in optionchainsym]
    modified_tokens = []
    for Symbol in optionchainsym:
        token = Symbol['token']
        modified_token = 'NFO|' + token
        modified_tokens.append(modified_token)

    print(modified_tokens)

    df = api.subscribe(modified_tokens)
    df = pd.DataFrame.from_dict(feedJson,orient='index', columns=['ltp', 'Tsym','openi','pdopeni'])
    print(df)

    while True:
        ce_buy_symbol,ce_sell_symbol,sell_strike,sell_price = get_closest_ltp_symbols(float(ltp_price)*2,symbol,option_type)
        if ce_buy_symbol != '':
            break
        sleep(30)

    place_orders(For_token,ce_buy_symbol,Strike,sell_strike,atm_expiry,atm_expiry,symbol,1,atm_token_lotsize,float(ltp_price),float(sell_price))
    
def place_orders(ce_buy_trading_symbol,ce_sell_trading_symbol,ce_buy_strike,ce_sell_strike,ce_buy_expiry,ce_sell_expiry,symbol,lot_multiple,lot_size,buy_price,sell_price) :
        
    ''' if symbol == 'Nifty':
        quantity_ce_buy = lot_multiple *lot_size*2
        quantity_ce_sell = lot_multiple *lot_size
    else:
        quantity_ce_buy = lot_multiple *lot_size*2
        quantity_ce_sell = lot_multiple *lot_size '''

    quantity_ce_buy = lot_multiple *lot_size*2
    quantity_ce_sell = lot_multiple *lot_size
    ##placing orders*************************************************
    ce_order=api.place_order(buy_or_sell='B', product_type='M',
                        exchange='NFO', tradingsymbol=ce_buy_trading_symbol, 
                        quantity=quantity_ce_buy, discloseqty=0,price_type='MKT', price=buy_price, trigger_price=None,
                        retention='DAY', remarks='ce_order_buy_001')
    
    pe_order=api.place_order(buy_or_sell='S', product_type='M',
                        exchange='NFO', tradingsymbol=ce_sell_trading_symbol, 
                        quantity=quantity_ce_sell, discloseqty=0,price_type='MKT', price=sell_price, trigger_price=None,
                        retention='DAY', remarks='ce_order_sell_001')
    ce_order_buy_id=ce_order['norenordno']
    pe_order_sell_id=pe_order['norenordno']
    

   
    stockitembullish = stockitem(ce_buy_trading_symbol,ce_order,buy_price,quantity_ce_buy,'BUY',False,False,0.0,'buy',ce_buy_strike,ce_buy_expiry)   
    stockitembearish = stockitem(ce_sell_trading_symbol,pe_order,sell_price,quantity_ce_sell,'SELL',False,False,0.0,'sell',ce_sell_strike,ce_sell_expiry)

    insertordersexecuted(stockitembullish)
    insertordersexecuted(stockitembearish)

    return(ce_order_buy_id,pe_order_sell_id)
    

def insertordersexecuted(stockitm):
    orders=[]

    orders.append({"TradingSymbol":stockitm.instrument_token,"OrderId":stockitm.order_id,"Qty":stockitm.quantity,"Ltp":stockitm.last_price,"OrderType":stockitm.ordertype,
                    "TpHit":stockitm.tp_hit,"SlHit":stockitm.sl_hit,"FinalPrice":stockitm.final_price,"ProductType":stockitm.producttype,"TradedDate":stockitm.traded_date,
                    "FinalTradedDate":stockitm.final_traded_date,"Strike":stockitm.strike,"Expiry":stockitm.expiry})
    
    x = client[databasename][collectionname].insert_many(orders)

def insert_orders_into_Mongodb():
    pass

def get_expiry_dates(exchange, symbol):
    import re
    import datetime
    sd = api.searchscrip(exchange, symbol)
    sd = (sd['values'])
    tsym_values = [Symbol['tsym'] for Symbol in sd]
    dates = [re.search(r'\d+[A-Z]{3}\d+', tsym).group() for tsym in tsym_values]
    formatted_dates = [datetime.datetime.strptime(date, '%d%b%y').strftime('%Y-%m-%d') for date in dates]
    sorted_formatted_dates = sorted(formatted_dates)
    sorted_dates = [datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d%b%y').upper() for date in sorted_formatted_dates]
    expiry_dates = sorted_dates
    return expiry_dates



def get_closest_ltp_symbols(ltp_value,symbol,opt_type):
    closest_symbols_c=""
    closest_symbols_p=""
    sell_strike=0
    sell_price=0

    if feedJson:
        df = pd.DataFrame.from_dict(feedJson,orient='index', columns=['ltp', 'Tsym','openi','pdopeni'])
        #df.to_csv('dataframe_Nifty.csv')
        df['diff'] = abs(df['ltp'] - ltp_value)
        df_c = df[df['Tsym'].str.contains(opt_type)]
        if not df_c.empty:
            min_diff_c = df_c['diff'].min()
            closest_symbols_c = df_c[df_c['diff'] == min_diff_c]['Tsym'].values[0]
            sell_strike = closest_symbols_c.split(opt_type)[-1]
            sell_price = df_c[df_c['diff'] == min_diff_c]['ltp'].values[0]
            print('Sell Strike - ')
            print(sell_strike)
            print('Closest strike Symbol - ')
            print(closest_symbols_c)
            print('Sell Price - ')
            print(sell_price)
    return closest_symbols_c,closest_symbols_p,sell_strike,sell_price

if __name__ == '__main__':
    #init()
    #options_Buy_ATM_Calls_Sell_DeepITM_Call('Nifty')
    #get_token_from_symbol('NSE:OFSS')
    options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:Nifty','P')
    #options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:Nifty Bank')
    #options_Buy_ATM_Calls_Sell_DeepITM_Call('OFSS')
    #while True:
        #sleep(60)
        #closest_symbols_c,closest_symbols_p = get_closest_ltp_symbols(190)
        #print(closest_symbols_c)
        #print(closest_symbols_p)
        
