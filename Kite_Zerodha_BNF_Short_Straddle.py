import logging
from datetime import datetime
import time

from dateutil.relativedelta import relativedelta, TH
from kiteconnect import KiteConnect

import schedule

from kite_trade import *
from ChartInk_Scaper_FileWatcher_Processor import stockitem

import helper

config = helper.read_config()

mongodbclient = config['MongoDBSettings']['mongodbclient']
databasename = config['MongoDBSettings']['databasename']
collectionname = config['MongoDBSettings']['collectionname']
enctoken=config['KiteSettings']['enctoken']

def get_kite():
    #kiteObj = KiteConnect(api_key='API_KEY')
    #kiteObj.set_access_token('ACCESS_TOKEN')

    #enctoken =  "rPb/WvduQsagTsiNtGYWWzNDuTYRv1vo6K276SlzRqSOCpRVs0lM+2YTGDWZXrwnuMv35qUWCNVHQQiHGh6D9B1mESHeTRaZUG0Z+ZfX/P0MA6j5K8ZsTA=="

    logging.basicConfig(filename="19_02_2023.log",format='%(levelname)s:%(message)s', level=logging.DEBUG)
    logging.debug('This message should appear on the console')
    logging.info('So should this')
    logging.warning('And this, too')    

    kiteObj = KiteApp(enctoken=enctoken)
    return kiteObj


kite = get_kite()
instrumentsList = None


def getCMP(tradingSymbol):
    quote = kite.quote(tradingSymbol)
    if quote:
        return quote[tradingSymbol]['last_price']
    else:
        return 0


def get_symbols(expiry, name, strike, ins_type):
    global instrumentsList
    instru=''
    if instrumentsList is None:
        instrumentsList = kite.instruments('NFO')

    lst_b = [num for num in instrumentsList if num['expiry'] == expiry and num['strike'] == strike
             and num['instrument_type'] == ins_type and num['name'] == name]
    if lst_b is not None and len(lst_b) != 0:
        instru = lst_b[0]['tradingsymbol']
    return instru


def place_order(tradingSymbol, price, qty, direction, exchangeType, product, orderType):
    try:
        orderId = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=exchangeType,
            tradingsymbol=tradingSymbol,
            transaction_type=direction,
            quantity=qty,
            price=price,
            product=product,
            order_type=orderType)

        logging.info('Order placed successfully, orderId = %s', orderId)
        return orderId
    except Exception as e:
        logging.info('Order placement failed: %s', e.message)

def insertordersexecuted(stockitm):
    import pymongo
    import certifi
    import datetime
    global client
    global orders

    client = pymongo.MongoClient(mongodbclient,tlsCAFile=certifi.where())
    orders=[]

    orders.append({"TradingSymbol":stockitm.instrument_token,"Qty":stockitm.quantity,"Ltp":stockitm.last_price,"OrderType":stockitm.ordertype,
                    "TpHit":stockitm.tp_hit,"SlHit":stockitm.sl_hit,"FinalPrice":stockitm.final_price,"ProductType":stockitm.producttype,"TradedDate":datetime.datetime.now()})
    x = client[databasename][collectionname].insert_many(orders)

def createshortstraddlebnf():
    # Find ATM Strike of Nifty
    #atm_strike = round(getCMP('NSE:NIFTY 50'), -2)
    atm_strike = round(getCMP('NFO:BANKNIFTY23MARFUT'), -2)

    next_thursday_expiry = datetime.today() + relativedelta(weekday=TH(1))

    symbol_ce = get_symbols(next_thursday_expiry.date(), 'BANKNIFTY', atm_strike, 'CE')
    symbol_pe = get_symbols(next_thursday_expiry.date(), 'BANKNIFTY', atm_strike, 'PE')

    place_order(symbol_ce, 0, 25, kite.TRANSACTION_TYPE_SELL, KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
                KiteConnect.ORDER_TYPE_MARKET)
    ltp = kite.ltp(symbol_ce)
    if ltp != None:
        stockitembullish = stockitem(symbol_ce,ltp,25,'SELL',False,False,0.0,'sell')
    else:
        stockitembullish = stockitem(symbol_ce,0.0,25,'SELL',False,False,0.0,'sell')    

    insertordersexecuted(stockitembullish)
    place_order(symbol_pe, 0, 25, kite.TRANSACTION_TYPE_SELL, KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
                KiteConnect.ORDER_TYPE_MARKET) 

    ltp = getCMP(symbol_pe)
    if ltp != None:
        stockitembearish = stockitem(symbol_pe,ltp,25,'SELL',False,False,0.0,'sell')
    else:
        stockitembearish = stockitem(symbol_pe,0.0,25,'SELL',False,False,0.0,'sell')    

    insertordersexecuted(stockitembearish)

if __name__ == '__main__':
    atm_strike = round(getCMP('NFO:BANKNIFTY29MARFUT'), -2)
    schedule.every().day.at("09:20").do(createshortstraddlebnf)
    schedule.every().day.at("09:50").do(createshortstraddlebnf)
    schedule.every().day.at("10:10").do(createshortstraddlebnf)
    schedule.every().day.at("10:45").do(createshortstraddlebnf)

    while True:
     
    # Checks whether a scheduled task
    # is pending to run or not
        schedule.run_pending()
        time.sleep(1)