import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

from kite_trade import *

maxitemcount=4
tradedstocks=None

class stockitem:
    def __init__(self, instrument_token, last_price,quantity,ordertype,tphit,slhit,finalprice,producttype):
        self.instrument_token = instrument_token
        self.last_price = last_price
        self.quantity =quantity
        self.ordertype = ordertype
        if self.last_price is not None:
            self.tp_value=self.last_price+self.last_price*0.05
            self.sl_value=self.last_price-self.last_price*0.025
        self.tp_hit=False
        self.sl_hit=False
        self.final_price=0.0
        self.final_value=0.0
        self.producttype = producttype

    def getfinalvalue(self):
        self.final_value = self.quantity*self.final_price
        return self.final_value    


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
    df_bullish = file_dict['bullish-screeners']
    df_bullish['OccurInDiffScreeners'] = df_bullish.groupby(by="nsecode")['nsecode'].transform('count')
    df_bullish = df_bullish.query(f'OccurInDiffScreeners >{maxitemcount}')
    df_bullish.drop(['sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
    grp_bullish =  df_bullish.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
    grp_bullish = grp_bullish[grp_bullish['OccurInDiffScreeners'] >maxitemcount].sort_values(['OccurInDiffScreeners'],ascending=False)

    df_bearish = file_dict['bearish-screeners']
    df_bearish['OccurInDiffScreeners'] = df_bearish.groupby(by="nsecode")['nsecode'].transform('count')
    df_bearish = df_bearish.query(f'OccurInDiffScreeners >{maxitemcount}')
    df_bearish.drop(['sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
    grp_bearish =  df_bearish.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
    grp_bearish = grp_bearish[grp_bearish['OccurInDiffScreeners'] >maxitemcount].sort_values(['OccurInDiffScreeners'],ascending=False)
    #grp_bullish.empty()

    df_bullish_intraday = file_dict['intraday-bullish-screeners']
    df_bullish_intraday['OccurInDiffScreeners'] = df_bullish_intraday.groupby(by="nsecode")['nsecode'].transform('count')
    df_bullish_intraday = df_bullish_intraday.query(f'OccurInDiffScreeners >{maxitemcount}')
    df_bullish_intraday.drop(['sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
    grp_bullish_intraday =  df_bullish_intraday.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
    grp_bullish_intraday = grp_bullish_intraday[grp_bullish_intraday['OccurInDiffScreeners'] >maxitemcount].sort_values(['OccurInDiffScreeners'],ascending=False)

    df_bearish_intraday = file_dict['intraday-bearish-screeners']
    df_bearish_intraday['OccurInDiffScreeners'] = df_bearish_intraday.groupby(by="nsecode")['nsecode'].transform('count')
    df_bearish_intraday = df_bearish_intraday.query(f'OccurInDiffScreeners >{maxitemcount}')
    df_bearish_intraday.drop(['sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
    grp_bearish_intraday =  df_bearish_intraday.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
    grp_bearish_intraday = grp_bearish_intraday[grp_bearish_intraday['OccurInDiffScreeners'] >maxitemcount].sort_values(['OccurInDiffScreeners'],ascending=False)

    tradeusingkite(grp_bullish,grp_bearish,df_bullish_intraday,df_bearish_intraday)

def getquantityfromltp(ltp,symbol):
    if symbol == "NSE:ROML":
        return 1
    if symbol == "NSE:MASKINVEST":
        return 1
    if ltp is None:
        return 1
    else:
        if ltp[symbol]['last_price'] != 0.0:
            return int(10000/ltp[symbol]['last_price'])
        else:
            return 1

def gettradedstocks():
    import pymongo
    import certifi
    import pandas as pd

    client = pymongo.MongoClient("mongodb+srv://TradingUser:Akshara66*@cluster0.tosvjw6.mongodb.net/?retryWrites=true&w=majority",tlsCAFile=certifi.where())
    tradedstocks = pd.DataFrame(list(client["ChartInkTradeLog"]["10_02_2023"].find({})))
    return tradedstocks

def insertordersexecuted(stockitm):
    import pymongo
    import certifi
    import datetime
    global client
    global orders

    client = pymongo.MongoClient("mongodb+srv://TradingUser:Akshara66*@cluster0.tosvjw6.mongodb.net/?retryWrites=true&w=majority",tlsCAFile=certifi.where())
    orders=[]

    orders.append({"TradingSymbol":stockitm.instrument_token,"Qty":stockitm.quantity,"Ltp":stockitm.last_price,"OrderType":stockitm.ordertype,
                    "TpHit":stockitm.tp_hit,"SlHit":stockitm.sl_hit,"FinalPrice":stockitm.final_price,"ProductType":stockitm.producttype,"TradedDate":datetime.datetime.now()})
    x = client["ChartInkTradeLog"]["10_02_2023"].insert_many(orders)

def tradeusingkite(bullish,bearish,intradaybullish,intradaybearish):
    print(bullish['nsecode'])
    print(bullish['OccurInDiffScreeners'])
    
    import pandas as pd
    #enctoken = "zIHb6tJAjlPNKlWePko2v4RKCp8G9kKll4X5KTeGx16/xMjPb2pieapxQUxdmxZ8NaPiZhv3LQscrvFfpHb5wujmx3H+TNRW430TliWs/NHlwo10Vd+ywQ=="
    enctoken =  "ORKPV7HB46RCDV9q5NYwLibZ6cXpAWJgMikbMZuGYdb4EQAR+kJqoh9o9mWwRTQmRFnwzRUwX99X08SNBb7MlHjXLAOZESU5KXzdtyT8ECmBUGsywbMGFA=="
    kite = KiteApp(enctoken=enctoken)

    #print(kite.quote(["NSE:NIFTY BANK", "NSE:ACC", "NFO:NIFTY22SEPFUT"]))

    stockitems=[]
    symbol = ""
    df =  gettradedstocks()
    if df is  None or len(df) <= 20:
        for index in range(0,5):
            if bullish.empty == False:
                if index <= bullish.shape[0] and bullish.iloc[index].empty == False:
                    print(symbol)
                    symbol= bullish.iloc[index]['nsecode']

                    #if len(stockitems) != 0:
                    #df = pd.DataFrame(stockitems)
                    #df_1 = df[df['instrument_token'] == 'symbol']
                    #if df_1.empty() is True:
                    ltp = kite.ltp("NSE:"+symbol)
                    qty = getquantityfromltp(ltp,"NSE:"+symbol)
                    if ltp != None:
                        stockitembullish = stockitem(symbol,ltp["NSE:"+symbol]['last_price'],qty,'BUY',False,False,0.0,'buy')
                    else:
                         stockitembullish = stockitem(symbol,0.0,qty,'BUY',False,False,0.0,'buy')    
                    # Place Order
                    order = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=symbol,
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
                                    tag="TradeViaPython")
                    #print("###########  Order_id       ###########==="+ order['data']+"  "+ order['error_type'])
                    insertordersexecuted(stockitembullish)
                    stockitems.append(stockitembullish)
                    print(order)
            if bearish.empty == False:
                if index <= bearish.shape[0] and bearish.iloc[index].empty == False:
                    print(symbol)
                    symbol= bearish.iloc[index]['nsecode']

                    #if len(stockitems) != 0:
                    #    df = pd.DataFrame(stockitems)
                    #    df_1 = df[df['instrument_token'] == 'symbol']
                    #    if df_1.empty() is True:
                    ltp = kite.ltp("NSE:"+symbol)
                    qty = getquantityfromltp(ltp,"NSE:"+symbol)
                    if ltp != None:
                        stockitembearish = stockitem(symbol,ltp["NSE:"+symbol]['last_price'],qty,'SELL',False,False,0.0,'sell')
                    else:
                        stockitembearish = stockitem(symbol,0.0,qty,'SELL',False,False,0.0,'sell')
                        

                    # Place Order
                    order = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=symbol,
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
                                    tag="TradeViaPython")
                    #print("###########  Order_id       ###########==="+ order['data']+"  "+ order['error_type'])
                    insertordersexecuted(stockitembearish)
                    stockitems.append(stockitembearish)
                    print(order)

            if intradaybearish.empty     == False:
                if index <= intradaybearish.shape[0] and intradaybearish.iloc[index].empty == False:
                    print(symbol)
                    symbol= intradaybearish.iloc[index]['nsecode']

                    #if len(stockitems) != 0:
                    #    df = pd.DataFrame(stockitems)
                    #    df_1 = df[df['instrument_token'] == 'symbol']
                    #    if df_1.empty() is True:
                    ltp = kite.ltp("NSE:"+symbol)
                    qty = getquantityfromltp(ltp,"NSE:"+symbol)
                    if ltp != None:
                        stockitemintradaybearish = stockitem(symbol,ltp["NSE:"+symbol]['last_price'],qty,'SELL',False,False,0.0,'intradaysell')
                        
                    else:
                        stockitemintradaybearish = stockitem(symbol,0.0,qty,'SELL',False,False,0.0,'intradaysell')

        # Place Order
                    order = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=symbol,
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
                                    tag="TradeViaPython")
                    #print("###########  Order_id       ###########==="+ order['data']+"  "+ order['error_type'])
                    insertordersexecuted(stockitemintradaybearish)
                    stockitems.append(stockitemintradaybearish)
                    print(order)

            if intradaybullish.empty == False:
                if index <= intradaybullish.shape[0] and intradaybullish.iloc[index].empty == False:
                    print(symbol)
                    symbol= intradaybullish.iloc[index]['nsecode']

                    #if len(stockitems) != 0:
                    #    df = pd.DataFrame(stockitems)
                    #    df_1 = df[df['instrument_token'] == 'symbol']
                    #    if df_1.empty() is True:
                    ltp = kite.ltp("NSE:"+symbol)
                    qty = getquantityfromltp(ltp,"NSE:"+symbol)
                    if ltp != None:
                        if symbol == 'NSE:MASKINVEST' :
                            stockitemintradaybullish = stockitem(symbol,0.0,qty,'BUY',False,False,0.0,'intradaybuy')
                        else:
                            stockitemintradaybullish = stockitem(symbol,ltp["NSE:"+symbol]['last_price'],qty,'BUY',False,False,0.0,'intradaybuy')
                    else:
                        stockitemintradaybullish = stockitem(symbol,0.0,qty,'BUY',False,False,0.0,'intradaybuy')

        # Place Order
                    order = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=symbol,
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
                                    tag="TradeViaPython")
                    #print("###########  Order_id       ###########==="+ order['data']+"  "+ order['error_type'])
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


if __name__ == '__main__':
    w = Watcher()
    w.run()

