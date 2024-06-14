import time
import schedule
import helper
import logging
import pandas as pd
from kite_trade import *
from Utils import stockitem
from producer import publish
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
#from Finvasia_Get_Strike_From_Given_Premium import options_buy_index_stock ,options_Buy_ATM_Call_Sell_Deep_OTM_Calls,ShoonyaApiPy,init,options_short_straddle
from Finvasia_Get_Strike_From_Given_Premium import finvasia_trading_helper
from Utils import process, processnewfiles, convertdataframe,stock_alert_notifier
    
#from Scrip_Count_Display import process

global file_dict

config = helper.read_config()
log_filename_path = config["Logger"]["LogFilePath"]
log_file_Name = config["Logger"]["LogFileName"]
mongodbclient = config["MongoDBSettings"]["mongodbclient"]
databasename = config["MongoDBSettings"]["databasename"]
collectionname = config["MongoDBSettings"]["collectionname"]
enctoken = config["KiteSettings"]["enctoken"]
maxitemcount = config["ChartinkscraperSettings"]["maxitemcount"]
pos_maxbackdays_count = config["ChartinkscraperSettings"]["positional_maxbackdays"]
pos_maxitem_count = config["ChartinkscraperSettings"]["positional_maxitemcount"]
pos_today_maxitemcount = config["ChartinkscraperSettings"]["positional_today_maxitemcount"]
intraday_today_maxitemcount = config["ChartinkscraperSettings"]["intraday_today_maxitemcount"]

# global stock count for max back days counts
maxitemcount = int(maxitemcount)
pos_maxbackdays_count = int(pos_maxbackdays_count)
pos_maxitem_count = int(pos_maxitem_count)
pos_today_maxitemcount = int(pos_today_maxitemcount)
intraday_today_maxitemcount = int(intraday_today_maxitemcount)
tradedstocks = None
bull_positional_df=pd.DataFrame()
bear_positional_df=pd.DataFrame()
bull_intra_df=pd.DataFrame()
bear_intra_df=pd.DataFrame()
bull_trade = True
# global stock count for today intra counts
bull_today_df=pd.DataFrame()
bear_today_df=pd.DataFrame()
bull_today_intra_df=pd.DataFrame()
bear_today_intra_df=pd.DataFrame()


logging.basicConfig(
        filename=log_filename_path + "//" + log_file_Name,
        format="%(asctime)s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level=20,
    )

logging.info(f"Maximum back days - {pos_maxbackdays_count}")
bull_positional_df,bear_positional_df,bull_intra_df,bear_intra_df = process(pos_maxbackdays_count)
if bull_positional_df.empty == False:
    bull_positional_df = convertdataframe(bull_positional_df)
if bear_positional_df.empty == False:
    bear_positional_df = convertdataframe(bear_positional_df)
if bull_intra_df.empty == False:
    bull_intra_df = convertdataframe(bull_intra_df)
if bear_intra_df.empty == False:
    bear_intra_df = convertdataframe(bear_intra_df)

stock_alert_notifier(bull_positional_df.to_string())
stock_alert_notifier(bear_positional_df.to_string())
stock_alert_notifier(bull_intra_df.to_string())
stock_alert_notifier(bear_intra_df.to_string())
def updatedataframesandtradescrips():
    global bull_trade 
    stockcount_df = pd.DataFrame()
    fth = finvasia_trading_helper()

    bull_today_df,bear_today_df,bull_today_intra_df,bear_today_intra_df = process(1)
    if bull_today_df.empty == False:
        bull_today_df = convertdataframe(bull_today_df)
    if bear_today_df.empty == False:
        bear_today_df = convertdataframe(bear_today_df)
    if bull_today_intra_df.empty == False:
        bull_today_intra_df = convertdataframe(bull_today_intra_df)
    if bear_today_intra_df.empty == False:
        bear_today_intra_df = convertdataframe(bear_today_intra_df)


    stock_alert_notifier(bull_today_df.to_string())
    stock_alert_notifier(bear_today_df.to_string())
    stock_alert_notifier(bull_today_intra_df.to_string())
    stock_alert_notifier(bear_today_intra_df.to_string())
    
# Read data from the files
    #stockcount_df = getcountdataframe(key)
    if bull_trade == True:
        if bull_positional_df is not None and bull_intra_df is not None and bull_today_df is not None and bull_today_intra_df is not None:
            # Check if a stock meets the criteria for bullish and intrabullish
            #bullish_stocks = bull_positional_df[bull_positional_df["OccurInDiffScreeners"] >= int(pos_maxitem_count)]["nsecode"]
            bull_today_stocks = bull_today_df[bull_today_df["OccurInDiffScreeners"] >= int(pos_today_maxitemcount)]["nsecode"]
            intrabull_today_stocks = bull_today_intra_df[bull_today_intra_df["OccurInDiffScreeners"] >= int(intraday_today_maxitemcount)]["nsecode"]

            #common_bullish = set(bullish_stocks) & set(bull_today_stocks) & set(intrabull_today_stocks) 
            common_bullish = set(bull_today_stocks) & set(intrabull_today_stocks) 
            if len(common_bullish) == 0:
                return
    
            symbol = "NSE:" + str(common_bullish.pop())
            print(f"Placing a BUY Order for CALL for the symbol-- {symbol}")
            stock_alert_notifier(f"Placing a BUY Order for CALL for the symbol-- {symbol}")
            logging.info(f"Placing a BUY Order for CALL for the symbol-- {symbol}")
            #init()
            #_ = options_buy_index_stock(symbol,"C","B")
            #mesg = ""
            finvasia_trading_helper.post_messages(f"3,{symbol},C")
            #options_Buy_ATM_Call_Sell_Deep_OTM_Calls(symbol,"C")
            #options_short_straddle(symbol,"C")
            bull_trade = False
    else:
        if bear_positional_df is not None and bear_intra_df is not None and bear_today_df is not None and bear_today_intra_df is not None:
            # Check if a stock meets the criteria for bearish and intrabearish
            #bearish_stocks = bear_positional_df[bear_positional_df["OccurInDiffScreeners"] >= int(pos_maxitem_count)]["nsecode"]
            bear_today_stocks = bear_today_df[bear_today_df["OccurInDiffScreeners"] >= int(pos_today_maxitemcount)]["nsecode"]
            intrabear_today_stocks = bear_today_intra_df[bear_today_intra_df["OccurInDiffScreeners"] >= int(intraday_today_maxitemcount)]["nsecode"]
            # Stocks meeting both criteria
            
            #common_bearish = set(bearish_stocks) & set(bear_today_stocks)  & set(intrabear_today_stocks)
            common_bearish = set(bear_today_stocks)  & set(intrabear_today_stocks)
            if len(common_bearish) == 0:
                return
            
            symbol = "NSE:" + str(common_bearish.pop())
            print(f"Placing a BUY Order for PUT for the symbol-- {symbol}")
            stock_alert_notifier(f"Placing a BUY Order for PUT for the symbol-- {symbol}")
            logging.info(f"Placing a BUY Order for PUT for the symbol-- {symbol}")
            #init()
            #_ = options_buy_index_stock(symbol,"P","B")
            finvasia_trading_helper.post_messages(f"3,{symbol},C")
            #options_Buy_ATM_Call_Sell_Deep_OTM_Calls(symbol,"P")
            #options_short_straddle(symbol,"C")
            bull_trade = True

        
    
def getcountdataframe(key):

    if key in file_dict.keys():
        df_bullish = file_dict[key]
        df_bullish["OccurInDiffScreeners"] = df_bullish.groupby(by="nsecode")[
            "nsecode"
        ].transform("count")
        df_bullish = df_bullish.query(f"OccurInDiffScreeners >{maxitemcount}")
        df_bullish.drop(
            ["sr", "per_chg", "close", "bsecode", "volume"], axis=1, inplace=True
        )
        grp_bullish = df_bullish.groupby("nsecode", as_index=False)[
            "OccurInDiffScreeners"
        ].max()
        grp_bullish = grp_bullish[
            grp_bullish["OccurInDiffScreeners"] > maxitemcount
        ].sort_values(["OccurInDiffScreeners"], ascending=False)

    return grp_bullish


def getquantityfromltp(ltp, symbol):
    try:
        if symbol == "NSE:ROML":
            return 1
        if symbol == "NSE:MASKINVEST":
            return 1
        if ltp is None:
            return 1
        else:
            if ltp[symbol]["last_price"] != 0.0:
                qty = 1
                if ltp[symbol]["last_price"] <= 2000.00:
                    return int(2000 / ltp[symbol]["last_price"])
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

    client = pymongo.MongoClient(mongodbclient, tlsCAFile=certifi.where())
    tradedstocks = pd.DataFrame(list(client[databasename][collectionname].find({})))
    return len(tradedstocks)


def insertordersexecuted(stockitm):
    import pymongo
    import certifi
    import datetime

    global client
    global orders

    client = pymongo.MongoClient(mongodbclient, tlsCAFile=certifi.where())
    orders = []

    orders.append(
        {
            "TradingSymbol": stockitm.instrument_token,
            "OrderId": stockitm.order_id,
            "Qty": stockitm.quantity,
            "Ltp": stockitm.last_price,
            "OrderType": stockitm.ordertype,
            "TpHit": stockitm.tp_hit,
            "SlHit": stockitm.sl_hit,
            "FinalPrice": stockitm.final_price,
            "ProductType": stockitm.producttype,
            "TradedDate": stockitm.traded_date,
            "FinalTradedDate": stockitm.final_traded_date,
            "Strike": stockitm.strike,
            "Expiry": stockitm.expiry,
        }
    )
    x = client[databasename][collectionname].insert_many(orders)


def tradeusingkite(key, topstockstotrade):
    print(topstockstotrade["nsecode"])
    print(topstockstotrade["OccurInDiffScreeners"])

    import pandas as pd

    kite = KiteApp(enctoken=enctoken)

    stockitems = []
    symbol = ""
    product = ""
    order_type = ""
    product_type = ""
    transaction_type = None

    match key:
        case "bullish-screeners":
            product = kite.PRODUCT_CNC
            order_type = "BUY"
            product_type = "buy"
            transaction_type = kite.TRANSACTION_TYPE_BUY
        case "bearish-screeners":
            product = kite.PRODUCT_CNC
            order_type = "SELL"
            product_type = "sell"
            transaction_type = kite.TRANSACTION_TYPE_SELL
        case "intraday-bullish-screeners":
            product = kite.PRODUCT_MIS
            order_type = "BUY"
            product_type = "buy"
            transaction_type = kite.TRANSACTION_TYPE_BUY
        case "intraday-bearish-screeners":
            product = kite.PRODUCT_MIS
            order_type = "SELL"
            product_type = "sell"
            transaction_type = kite.TRANSACTION_TYPE_SELL

    df_count = gettradedstockscount()
    if df_count <= 200:
        for index in range(0, 5):
            if topstockstotrade.empty == False:
                if (
                    index < topstockstotrade.shape[0]
                    and topstockstotrade.iloc[index].empty == False
                ):
                    print(symbol)
                    symbol = topstockstotrade.iloc[index]["nsecode"]
                    symbol = "NSE:" + symbol
                    ltp = kite.ltp(symbol)

                    if ltp != None and len(ltp) > 0:
                        qty = getquantityfromltp(ltp, symbol)
                        stockitemtoinsert = stockitem(
                            symbol,
                            0,
                            ltp[symbol]["last_price"],
                            qty,
                            order_type,
                            False,
                            False,
                            0.0,
                            product_type,
                            0,
                            None,
                        )
                    else:
                        stockitemtoinsert = stockitem(
                            symbol,
                            0,
                            0.0,
                            1,
                            order_type,
                            False,
                            False,
                            0.0,
                            product_type,
                            0,
                            None,
                        )
                    # Place Order
                    stockitemtoinsert.order_id = kite_place_order(
                        symbol, transaction_type, qty, product
                    )

                    insertordersexecuted(stockitemtoinsert)
                    stockitems.append(stockitemtoinsert)
                    print(stockitemtoinsert.order_id)

def tradeusingfinvasia(key, topstockstotrade):
    
    match key:
        case "intraday-bullish-screeners":
            if topstockstotrade.empty == False:
                if (topstockstotrade.iloc[0].empty == False):
                    symbol = topstockstotrade.iloc[0]["nsecode"]
                    symbol = "NSE:" + symbol
                    options_buy_index_stock(symbol,"C")
            
        case "intraday-bearish-screeners":
            if topstockstotrade.empty == False:
                if (topstockstotrade.iloc[0].empty == False):
                    symbol = topstockstotrade.iloc[0]["nsecode"]
                    symbol = "NSE:" + symbol
                    options_buy_index_stock(symbol,"P")

def kite_place_order(symbol, transaction_type, qty, product):

    kite = KiteApp(enctoken=enctoken)
    try:

        order = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=kite.EXCHANGE_NSE,
            tradingsymbol=symbol.split(":")[1],
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
            tag="chartinkscraper",
        )
        if order is not None and order["status"] == "success":
            return order["data"]["order_id"]
        else:
            return 0
    except Exception as e:
        print(e.message)

''' 
def processnewfiles():
    import glob
    import numpy as np
    import os
    import pandas as pd
    from datetime import datetime

    global file_dict

    from ChartInk_Scrape_With_Multiprocess import screenmapper

    dfs = []

    df_1 = pd.DataFrame(
        columns=[
            "sr",
            "nsecode",
            "name",
            "bsecode",
            "per_chg",
            "close",
            "volume",
            "ScreenerName",
            "TimeOfDay",
        ]
    )
    df_2 = pd.DataFrame(
        columns=[
            "sr",
            "nsecode",
            "name",
            "bsecode",
            "per_chg",
            "close",
            "volume",
            "ScreenerName",
            "TimeOfDay",
        ]
    )

    from ChartInk_Scrape_With_Multiprocess import screenmapper

    todayfolder = datetime.now().strftime("%d_%m_%Y")

    all_files = glob.glob(
        "D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\"
        + todayfolder
        + "\*.csv"
    )

    file_dict = {}
    for i, filename in enumerate(all_files, start=0):
        file1 = filename.split("\\")[-1]
        file = file1.split("_")[3]
        key = file
        df = pd.read_csv(filename)
        df = removefirstcolumn(df)
        if file_dict.get(key) is None:
            file_dict[key] = pd.DataFrame()
        file_dict[key] = pd.concat([file_dict.get(key), df])

    for key, value in file_dict.items():
        filenameagg = key + "_" + todayfolder + ".csv"
        value.to_csv(filenameagg)
    # return df_1,df_2

 '''
class Watcher:

    DIRECTORY_TO_WATCH = (
        "D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\"
        + datetime.now().strftime("%d_%m_%Y")
        + "\\"
    )

    def __init__(self):
       #self.observer = Observer()
       pass

    def run(self):
        event_handler = Handler()
        self.observer = Observer()
        
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(60)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class stock_info:
    def __init__(self, sym, opttype):
        self.Symbol = sym
        self.OptionType = opttype


import json


def to_json(obj):
    return json.dumps(obj, default=lambda obj: obj.__dict__)


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == "created":
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)
            #processnewfiles()
            updatedataframesandtradescrips()

            ''' try:
                stk_info = stock_info("NSE:NIFTY", "C")
                # publish('Stock buy/sell triggered',to_json(stk_info))
                publish("Stock buy/sell triggered", "|" + "NSE:NIFTY" + "|" + "C")
            except:
                pass '''

        elif event.event_type == "modified":
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)


def startfilewatcher():
    try:
        w = Watcher()
        w.run()
    except Exception as e:
        pass


if __name__ == "__main__":
    try:
        logging.info('File Watcher started ...execution started now.....')

        #schedule.every().day.at("08:27").do(startfilewatcher)  #1628703.0 12_04_2024 13_04_2024

        logging.info("**********************************************************")
        logging.info(f'File Watcher started at ...execution started now.....')
        startfilewatcher()
        while True:
            #schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Logged out of the program using keyboard interrupt....")

    # startfilewatcher()
