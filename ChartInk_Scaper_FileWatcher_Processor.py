import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import pandas as pd

from kite_trade import *
import schedule
import helper

global file_dict

config = helper.read_config()

mongodbclient = config['MongoDBSettings']['mongodbclient']
databasename = config['MongoDBSettings']['databasename']
collectionname = config['MongoDBSettings']['collectionname']
enctoken=config['KiteSettings']['enctoken']
maxitemcount=config['ChartinkscraperSettings']['maxitemcount']

maxitemcount = int(maxitemcount)
tradedstocks=None

class stockitem:
    def __init__(self, instrument_token,order_id, last_price,quantity,ordertype,tphit,slhit,finalprice,producttype,strike=None,expiry=None):
        self.instrument_token = instrument_token
        self.order_id= order_id
        self.last_price = last_price
        self.quantity =quantity
        self.ordertype = ordertype
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

def removefirstcolumn(dataframeinput):
    first_column = dataframeinput.columns[0]
    # Delete first
    dataframeinput = dataframeinput.drop([first_column], axis=1)
    return dataframeinput

def updatedataframesandtradescrips():

    stockcount_df=pd.DataFrame()
    for key ,value in file_dict.items():
        print("key=", key)
        stockcount_df = getcountdataframe(key)
        #tradeusingkite(grp_bullish,grp_bearish,df_bullish_intraday,df_bearish_intraday)
        tradeusingkite(key,stockcount_df)
        print(value)

def getcountdataframe(key):

    if key in file_dict.keys():
        df_bullish = file_dict[key]
        df_bullish['OccurInDiffScreeners'] = df_bullish.groupby(by="nsecode")['nsecode'].transform('count')
        df_bullish = df_bullish.query(f'OccurInDiffScreeners >{maxitemcount}')
        df_bullish.drop(['sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
        grp_bullish =  df_bullish.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
        grp_bullish = grp_bullish[grp_bullish['OccurInDiffScreeners'] >maxitemcount].sort_values(['OccurInDiffScreeners'],ascending=False)

    return grp_bullish

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
                if ltp[symbol]['last_price'] <= 2000.00:
                    return int(2000/ltp[symbol]['last_price'])
                else:
                    return qty
            else:
                return 1

    except Exception as ex:
        pass

def gettradedstockscount():
    import pymongo
    import certifi
    import pandas as pd

    client = pymongo.MongoClient(mongodbclient,tlsCAFile=certifi.where())
    tradedstocks = pd.DataFrame(list(client[databasename][collectionname].find({})))
    return len(tradedstocks)

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
                    "FinalTradedDate":stockitm.final_traded_date,"Strike":stockitm.strike,"Expiry":stockitm.expiry})
    x = client[databasename][collectionname].insert_many(orders)


def tradeusingkite(key,topstockstotrade):
    print(topstockstotrade['nsecode'])
    print(topstockstotrade['OccurInDiffScreeners'])
    
    import pandas as pd
    kite = KiteApp(enctoken=enctoken)

    stockitems=[]
    symbol = ""
    product=""
    order_type=""
    product_type=""
    transaction_type=None

    match key:
        case "bullish-screeners":
            product = kite.PRODUCT_CNC
            order_type= "BUY"
            product_type="buy"
            transaction_type = kite.TRANSACTION_TYPE_BUY
        case "bearish-screeners":
            product = kite.PRODUCT_CNC
            order_type= "SELL"
            product_type="sell"
            transaction_type = kite.TRANSACTION_TYPE_SELL
        case "intraday-bullish-screeners":
            product = kite.PRODUCT_MIS
            order_type= "BUY"
            product_type="buy"
            transaction_type = kite.TRANSACTION_TYPE_BUY
        case "intraday-bearish-screeners":
            product = kite.PRODUCT_MIS
            order_type= "SELL"
            product_type="sell"
            transaction_type = kite.TRANSACTION_TYPE_SELL

    df_count =  gettradedstockscount()
    if df_count <= 200:
       for index in range(0,5):
            if topstockstotrade.empty == False:
                if index < topstockstotrade.shape[0] and topstockstotrade.iloc[index].empty == False:
                    print(symbol)
                    symbol= topstockstotrade.iloc[index]['nsecode']
                    symbol="NSE:"+symbol
                    ltp = kite.ltp(symbol)
                    
                    if ltp != None and len(ltp) > 0:
                        qty = getquantityfromltp(ltp,symbol)
                        stockitemtoinsert = stockitem(symbol,0,ltp[symbol]['last_price'],qty,order_type,False,False,0.0,product_type,0,None)
                    else:
                         stockitemtoinsert = stockitem(symbol,0,0.0,1,order_type,False,False,0.0,product_type,0,None)    
                    # Place Order
                    stockitemtoinsert.order_id = kite_place_order(symbol,transaction_type,qty,product)
                    
                    insertordersexecuted(stockitemtoinsert)
                    stockitems.append(stockitemtoinsert)
                    print(stockitemtoinsert.order_id)
            
def kite_place_order(symbol,transaction_type,qty,product):

    kite = KiteApp(enctoken=enctoken)
    try:

        order = kite.place_order(variety=kite.VARIETY_REGULAR,   
                exchange=kite.EXCHANGE_NSE, 
                tradingsymbol=symbol.split(':')[1], 
                transaction_type=transaction_type,
                quantity=qty,   
                product=product,   
                order_type=kite.ORDER_TYPE_MARKET,   
                price=None, 
                validity=None,  
                disclosed_quantity=None,    
                trigger_price=None, 
                squareoff=None, 
                stoploss=None,  
                trailing_stoploss=None, 
                tag="chartinkscraper")      
        if order is not None and order['status'] == 'success':
            return order['data']['order_id']
        else:
            return 0
    except Exception as e:
        print(e.message)


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
    startfilewatcher()

    
