import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

from kite_trade import *
import schedule
#maxitemcount=10
tradedstocks=None

class stockitem:
    def __init__(self, instrument_token,order_id, last_price,quantity,ordertype,tphit,slhit,finalprice,producttype,strike,expiry):
        self.instrument_token = instrument_token
        self.order_id= order_id
        self.last_price = last_price
        self.quantity =quantity
        self.ordertype = ordertype
        ''' if self.last_price is not None and len(self.last_price) != 0:
            self.tp_value=self.last_price+self.last_price*0.05
            self.sl_value=self.last_price-self.last_price*0.025 '''
        self.tp_hit=False
        self.sl_hit=False
        self.final_price=0.0
        self.final_value=0.0
        self.producttype = producttype
        self.strike=strike
        self.expiry=expiry
        self.traded_date=datetime.today()
        self.final_traded_date=datetime.today()

    def getfinalvalue(self):
        self.final_value = self.quantity*self.final_price
        return self.final_value    


import helper

config = helper.read_config()

mongodbclient = config['MongoDBSettings']['mongodbclient']
databasename = config['MongoDBSettings']['databasename']
collectionname = config['MongoDBSettings']['collectionname']
enctoken=config['KiteSettings']['enctoken']
maxitemcount=config['ChartinkscraperSettings']['maxitemcount']
maxitemcount = int(maxitemcount)


def removefirstcolumn(dataframeinput):
    first_column = dataframeinput.columns[0]
    # Delete first
    dataframeinput = dataframeinput.drop([first_column], axis=1)
    return dataframeinput

global file_dict

def updatedataframesandtradescrips():
    for key ,value in file_dict.items():
        print("key=", key)
        print(value)
    #pass
    if 'bullish-screeners' in file_dict.keys():
        df_bullish = file_dict['bullish-screeners']
        df_bullish['OccurInDiffScreeners'] = df_bullish.groupby(by="nsecode")['nsecode'].transform('count')
        df_bullish = df_bullish.query(f'OccurInDiffScreeners >{maxitemcount}')
        df_bullish.drop(['sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
        grp_bullish =  df_bullish.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
        grp_bullish = grp_bullish[grp_bullish['OccurInDiffScreeners'] >maxitemcount].sort_values(['OccurInDiffScreeners'],ascending=False)

    if 'bearish-screeners' in file_dict.keys():
        df_bearish = file_dict['bearish-screeners']
        df_bearish['OccurInDiffScreeners'] = df_bearish.groupby(by="nsecode")['nsecode'].transform('count')
        df_bearish = df_bearish.query(f'OccurInDiffScreeners >{maxitemcount}')
        df_bearish.drop(['sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
        grp_bearish =  df_bearish.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
        grp_bearish = grp_bearish[grp_bearish['OccurInDiffScreeners'] >maxitemcount].sort_values(['OccurInDiffScreeners'],ascending=False)
        #grp_bullish.empty()

    if 'intraday-bullish-screeners' in file_dict.keys():
        df_bullish_intraday = file_dict['intraday-bullish-screeners']
        df_bullish_intraday['OccurInDiffScreeners'] = df_bullish_intraday.groupby(by="nsecode")['nsecode'].transform('count')
        df_bullish_intraday = df_bullish_intraday.query(f'OccurInDiffScreeners >{maxitemcount}')
        df_bullish_intraday.drop(['sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
        grp_bullish_intraday =  df_bullish_intraday.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
        grp_bullish_intraday = grp_bullish_intraday[grp_bullish_intraday['OccurInDiffScreeners'] >maxitemcount].sort_values(['OccurInDiffScreeners'],ascending=False)

    if 'intraday-bearish-screeners' in file_dict.keys():

        df_bearish_intraday = file_dict['intraday-bearish-screeners']
        df_bearish_intraday['OccurInDiffScreeners'] = df_bearish_intraday.groupby(by="nsecode")['nsecode'].transform('count')
        df_bearish_intraday = df_bearish_intraday.query(f'OccurInDiffScreeners >{maxitemcount}')
        df_bearish_intraday.drop(['sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
        grp_bearish_intraday =  df_bearish_intraday.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
        grp_bearish_intraday = grp_bearish_intraday[grp_bearish_intraday['OccurInDiffScreeners'] >maxitemcount].sort_values(['OccurInDiffScreeners'],ascending=False)

    tradeusingkite(grp_bullish,grp_bearish,df_bullish_intraday,df_bearish_intraday)

def getquantityfromltp(ltp,symbol):
    try :
        if symbol == "NSE:ROML":
            return 1
        if symbol == "NSE:MASKINVEST":
            return 1
        if ltp is None:
            return 1
        else:
            if ltp[symbol]['last_price'] != 0.0:
                qty=1
                if ltp[symbol]['last_price'] <= 10000.00:
                    return int(10000/ltp[symbol]['last_price'])
                else:
                    return qty
            else:
                return 1

    except Exception as ex:
        pass

def gettradedstocks():
    import pymongo
    import certifi
    import pandas as pd

    client = pymongo.MongoClient(mongodbclient,tlsCAFile=certifi.where())
    tradedstocks = pd.DataFrame(list(client[databasename][collectionname].find({})))
    return tradedstocks

def insertordersexecuted(stockitm):
    import pymongo
    import certifi
    import datetime
    global client
    global orders

    client = pymongo.MongoClient(mongodbclient,tlsCAFile=certifi.where())
    orders=[]

    orders.append({"TradingSymbol":stockitm.instrument_token,"OrderId":stockitm.order_id,"Qty":stockitm.quantity,"Ltp":stockitm.last_price,"OrderType":stockitm.ordertype,
                    "TpHit":stockitm.tp_hit,"SlHit":stockitm.sl_hit,"FinalPrice":stockitm.final_price,"ProductType":stockitm.producttype,"TradedDate":stockitm.traded_date,
                    "FinalTradedDate":stockitm.final_traded_date})
    x = client[databasename][collectionname].insert_many(orders)

def tradeusingkite(bullish,bearish,intradaybullish,intradaybearish):
    print(bullish['nsecode'])
    print(bullish['OccurInDiffScreeners'])
    
    import pandas as pd

    kite = KiteApp(enctoken=enctoken)

    #print(kite.quote(["NSE:NIFTY BANK", "NSE:ACC", "NFO:NIFTY22SEPFUT"]))

    stockitems=[]
    symbol = ""
    df =  gettradedstocks()
    if df is  None or len(df) <= 20 :
        #maxitemcount:
        for index in range(0,5):
            if bullish.empty == False:
                if index < bullish.shape[0] and bullish.iloc[index].empty == False:
                    print(symbol)
                    symbol= bullish.iloc[index]['nsecode']

                    symbol="NSE:"+symbol
                    ltp = kite.ltp(symbol)
                    
                    if ltp != None and len(ltp) > 0:
                        qty = getquantityfromltp(ltp,symbol)
                        stockitembullish = stockitem(symbol,0,ltp[symbol]['last_price'],qty,'BUY',False,False,0.0,'buy',0,None)
                    else:
                         stockitembullish = stockitem(symbol,0,0.0,1,'BUY',False,False,0.0,'buy',0,None)    
                    # Place Order
                    order = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=symbol.split(':')[1],
                                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                                    quantity=qty,
                                    product=kite.PRODUCT_CNC,
                                    order_type=kite.ORDER_TYPE_MARKET,
                                    price=None,
                                    validity=None,
                                    disclosed_quantity=None,
                                    trigger_price=None,
                                    squareoff=None,
                                    stoploss=None,
                                    trailing_stoploss=None,
                                    tag="chartinkscraper")
                    #print("###########  Order_id       ###########==="+ order['data']+"  "+ order['error_type'])
                    if order['status'] == 'success':
                        stockitembullish.order_id = order['data']['order_id']
                    else:
                        stockitembullish.order_id = 0
                    insertordersexecuted(stockitembullish)
                    stockitems.append(stockitembullish)
                    print(order)
            if bearish.empty == False:
                if index < bearish.shape[0] and bearish.iloc[index].empty == False:
                    print(symbol)
                    symbol= bearish.iloc[index]['nsecode']
                    symbol="NSE:"+symbol

                    ltp = kite.ltp(symbol)
                    
                    if ltp != None and len(ltp) > 0:
                        qty = getquantityfromltp(ltp,symbol)
                        stockitembearish = stockitem(symbol,0,ltp[symbol]['last_price'],qty,'SELL',False,False,0.0,'sell',0,None)
                    else:
                        stockitembearish = stockitem(symbol,0,0.0,1,'SELL',False,False,0.0,'sell',0,None)
                        

                    # Place Order
                    order = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=symbol.split(':')[1],
                                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                                    quantity=qty,
                                    product=kite.PRODUCT_CNC,
                                    order_type=kite.ORDER_TYPE_MARKET,
                                    price=None,
                                    validity=None,
                                    disclosed_quantity=None,
                                    trigger_price=None,
                                    squareoff=None,
                                    stoploss=None,
                                    trailing_stoploss=None,
                                    tag="chartinkscraper")
                    #print("###########  Order_id       ###########==="+ order['data']+"  "+ order['error_type'])
                    if order['status'] == 'success':
                        stockitembearish.order_id = order['data']['order_id']
                    else:
                        stockitembearish.order_id = 0
                    insertordersexecuted(stockitembearish)
                    stockitems.append(stockitembearish)
                    print(order)

            if intradaybearish.empty     == False:
                if index < intradaybearish.shape[0] and intradaybearish.iloc[index].empty == False:
                    print(symbol)
                    symbol= intradaybearish.iloc[index]['nsecode']
                    symbol="NSE:"+symbol

                    ltp = kite.ltp(symbol)
                    
                    if ltp != None and len(ltp) > 0:
                        qty = getquantityfromltp(ltp,symbol)
                        stockitemintradaybearish = stockitem(symbol,0,ltp[symbol]['last_price'],qty,'SELL',False,False,0.0,'intradaysell',0,None)
                        
                    else:
                        stockitemintradaybearish = stockitem(symbol,0,0.0,1,'SELL',False,False,0.0,'intradaysell',0,None)

        # Place Order
                    order = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=symbol.split(':')[1],
                                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                                    quantity=qty,
                                    product=kite.PRODUCT_MIS,
                                    order_type=kite.ORDER_TYPE_MARKET,
                                    price=None,
                                    validity=None,
                                    disclosed_quantity=None,
                                    trigger_price=None,
                                    squareoff=None,
                                    stoploss=None,
                                    trailing_stoploss=None,
                                    tag="chartinkscraper")
                    #print("###########  Order_id       ###########==="+ order['data']+"  "+ order['error_type'])
                    if order['status'] == 'success':
                        stockitemintradaybearish.order_id = order['data']['order_id']
                    else:
                        stockitemintradaybearish.order_id = 0
                    insertordersexecuted(stockitemintradaybearish)
                    stockitems.append(stockitemintradaybearish)
                    print(order)

            if intradaybullish.empty == False:
                if index < intradaybullish.shape[0] and intradaybullish.iloc[index].empty == False:
                    print(symbol)
                    symbol= intradaybullish.iloc[index]['nsecode']
                    symbol="NSE:"+symbol

                    ltp = kite.ltp(symbol)
                    
                    if ltp != None and len(ltp) > 0:
                        if symbol == 'NSE:MASKINVEST' :

                            stockitemintradaybullish = stockitem(symbol,0,0.0,1,'BUY',False,False,0.0,'intradaybuy',0,None)
                        else:
                            qty = getquantityfromltp(ltp,symbol)
                            stockitemintradaybullish = stockitem(symbol,0,ltp[symbol]['last_price'],qty,'BUY',False,False,0.0,'intradaybuy',0,None)
                    else:
                        stockitemintradaybullish = stockitem(symbol,0,0.0,1,'BUY',False,False,0.0,'intradaybuy',0,None)

        # Place Order
                    order = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=symbol.split(':')[1],
                                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                                    quantity=qty,
                                    product=kite.PRODUCT_MIS,
                                    order_type=kite.ORDER_TYPE_MARKET,
                                    price=None,
                                    validity=None,
                                    disclosed_quantity=None,
                                    trigger_price=None,
                                    squareoff=None,
                                    stoploss=None,
                                    trailing_stoploss=None,
                                    tag="chartinkscraper")
                    #print("###########  Order_id       ###########==="+ order['data']+"  "+ order['error_type'])
                    if order['status'] == 'success':
                        stockitemintradaybullish.order_id = order['data']['order_id']
                    else:
                        stockitemintradaybullish.order_id = 0
                    insertordersexecuted(stockitemintradaybullish)
                    stockitems.append(stockitemintradaybullish)
                    print(order)


def processnewfiles():
    import glob
    import numpy as np
    import os
    import pandas as pd
    from datetime import datetime
    global file_dict

    from ChartInk_Scrape_With_Multiprocess import screenmapper
    dfs=[]

    df_1=pd.DataFrame(columns=['sr','nsecode','name','bsecode','per_chg','close','volume','ScreenerName','TimeOfDay'])
    df_2=pd.DataFrame(columns=['sr','nsecode','name','bsecode','per_chg','close','volume','ScreenerName','TimeOfDay'])

    from ChartInk_Scrape_With_Multiprocess import screenmapper
    todayfolder = datetime.now().strftime("%d_%m_%Y")
    
    all_files = glob.glob("D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\"+todayfolder+"\*.csv")
    
    file_dict={}
    for i,filename in enumerate(all_files, start=0):
        file1 = filename.split('\\')[-1]
        file = file1.split('_')[3]
        key = file
        df = pd.read_csv(filename)
        df = removefirstcolumn(df)
        if file_dict.get(key) is None:
            file_dict[key]= pd.DataFrame()
        file_dict[key] = pd.concat([file_dict.get(key),df])

    for key,value in file_dict.items():
        filenameagg = key+'_'+todayfolder+'.csv'
        value.to_csv(filenameagg)
    #return df_1,df_2




class Watcher:
    DIRECTORY_TO_WATCH = "D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\"+datetime.now().strftime("%d_%m_%Y")+"\\"
    
    #DIRECTORY_TO_WATCH = "D:/Python_Trader_Code/24_12_2022/"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(60)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print ("Received created event - %s." % event.src_path)
            processnewfiles()
            updatedataframesandtradescrips()

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print ("Received modified event - %s." % event.src_path)

def startfilewatcher():
    try:
        w = Watcher()
        w.run()
    except Exception as e:
        pass

if __name__ == '__main__':

    #schedule.every().day.at("18:13").do(startfilewatcher)
    startfilewatcher()

    
