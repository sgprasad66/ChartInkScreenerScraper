import time
import pandas as pd
import helper
import pymongo
import certifi
import datetime as dt
import time
import pyotp
import schedule
import logging
import numpy as np
from time import sleep
from datetime import datetime
from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime, timedelta
from chartink_through_python import CreateCsvFile
import win32pipe, win32file, pywintypes
from Unique_Number_Gen import generate_unique_number
from multiprocessing import Queue
import multiprocessing
import threading
from Utils import MultiLegStrategy,start_service,stop_service,stockitem,json_file_repository,get_traded_records,update_trades,get_sl_tp_values
import random, time

# IPC parameters
PIPE_NAME = r"\\.\pipe\simple-ipc-pipe"
ENCODING = "ascii"

global candlestick_data
global optidx_or_optstk
candlestick_data = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close"])

''' pipe = win32pipe.CreateNamedPipe(
    PIPE_NAME,
    win32pipe.PIPE_ACCESS_DUPLEX,
    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE,
    1,
    65536,
    65536,
    0,
    None,
) '''

pd.set_option("display.max_rows", None)
config = helper.read_config()
repository_setting=config["RepositorySettings"]["RepositoryMode"]
mongodbclient = config["MongoDBSettings"]["mongodbclient"]
databasename = config["MongoDBSettings"]["databasename"]
collectionname = config["MongoDBSettings"]["collectionname"]
deletecollectionname = config["MongoDBSettings"]["deletecollectionname"]
log_filename_path = config["Logger"]["LogFilePath"]
log_file_Name = config["Logger"]["LogFileName"]
lots_multiplier = config["SLandTPSettings"]["lots_multiplier"]

feed_opened = False
socket_opened = False
feedJson = {}
candlestick_data_dict = {}
global_lock = False
spot_tokens = []
lock = multiprocessing.Lock()


#client = pymongo.MongoClient(mongodbclient,tlsCAFile=certifi.where())
#print(certifi.where())
client = pymongo.MongoClient(mongodbclient, ssl=False)


class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(
            self,
            host="https://api.shoonya.com/NorenWClientTP/",
            websocket="wss://api.shoonya.com/NorenWSTP/",
        )

logging.basicConfig(
        filename=log_filename_path + "//" + log_file_Name,
        #format="%(asctime)s %(message)s",
        format = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level=20,
    )

class finvasia_trading_helper:

    trading_message_queue = multiprocessing.Queue()
    socket_rt_df=pd.DataFrame()
    
    logging.info("Logging in to the Finvasia API system")

    def __init__(self):
        #self.thread_process = threading.Thread()
        self.thread_process = threading.Thread(target=self.process_messages, args=(self.trading_message_queue,))
        self.thread_process.daemon = True
        self.thread_process.start()

        self.thread_update = threading.Thread(target=self.update_trade_prices, args=())
        self.thread_update.daemon = True
        self.thread_update.start()

        self.api = ShoonyaApiPy()
        user = ""
        pwd = ""
        vc = ""
        app_key = "acf591571dae1737ac28495698e2eaf1"
        token = "54F7Y5B2H5N32W36TYFOJUD6W67U2W4V"
        global fno_scrips
        time.sleep(2)
        while True:
            try:
                factor2 = pyotp.TOTP(token).now()
                ret = self.api.login(
                    userid=user,
                    password=pwd,
                    twoFA=factor2,
                    vendor_code=vc,
                    api_secret=app_key,
                    imei="00:FF:7E:4B:40:1E",
                )
                if ret["stat"] == "Ok":
                    print("login successful")
                    break
            except Exception:
                print("could not login, retrying")
                time.sleep(2)
                continue
        self.setupWebSocket()
#def init():

    

#init()


    def event_handler_feed_update(self,tick_data):
        lock.acquire()
        UPDATE = False
        if "tk" in tick_data:
            token = tick_data["tk"]
            timest = datetime.fromtimestamp(int(tick_data["ft"])).isoformat()
            feed_data = {"tt": timest}
            feed_data_agg = {"tt": timest}
            if "lp" in tick_data:
                feed_data["ltp"] = float(tick_data["lp"])
                feed_data_agg["ltp"] = float(tick_data["lp"])
            else:
                # feed_data_agg['ltp'] = 0.0
                pass
            if "ts" in tick_data:
                feed_data["Tsym"] = str(tick_data["ts"])
                feed_data_agg["Tsym"] = str(tick_data["ts"])
            else:
                feed_data_agg["Tsym"] = ""
            if "oi" in tick_data:
                feed_data["openi"] = float(tick_data["oi"])
                feed_data_agg["openi"] = float(tick_data["oi"])
            else:
                feed_data_agg["openi"] = 0.0
            if "poi" in tick_data:
                feed_data["pdopeni"] = str(tick_data["poi"])
                feed_data_agg["pdopeni"] = str(tick_data["poi"])
            else:
                feed_data_agg["pdopeni"] = ""
            if "v" in tick_data:
                feed_data["Volume"] = int(tick_data["v"])
                feed_data_agg["Volume"] = int(tick_data["v"])
            else:
                feed_data_agg["Volume"] = 0
            if feed_data:
                UPDATE = True
                if token not in feedJson:
                    feedJson[token] = {}
                feedJson[token].update(feed_data)
            # Concatenate the new data with the existing candlestick_data for the token
            if not global_lock:
                if token in spot_tokens:
                    if token not in candlestick_data_dict:
                        candlestick_data_dict[token] = {}

                    candlestick_data_dict[token][timest] = feed_data_agg
            if UPDATE:
                pass

        lock.release()


    def event_handler_order_update(self,order_update):
        pass  # print(f"order feed {order_update}")


    def open_callback(self):
        global feed_opened
        feed_opened = True
        print("Websocket opened")


    def setupWebSocket(self):
        global feed_opened
        print("waiting for socket opening")
        self.api.start_websocket(
            order_update_callback=self.event_handler_order_update,
            subscribe_callback=self.event_handler_feed_update,
            socket_open_callback=self.open_callback,
        )
        ''' while feed_opened == False:
            pass '''

#setupWebSocket()


    def get_token_from_symbol(self,exchange, symbol):
        global optidx_or_optstk
        symb_one_strike = 0
        symb_two_strike = 0
        strike_diff = 0
        token = 0
        #symbol = symbol+'-EQ'
        if not (symbol in ["Nifty","Nifty Bank"]):
            ret = self.api.searchscrip(exchange=exchange, searchtext=symbol+'-EQ')
            optidx_or_optstk = "OPTSTK"
        else:
            '''  if symbol== "Nifty":
                ret = api.searchscrip(exchange=exchange, searchtext="Nifty 50")
            else: '''
            ret = self.api.searchscrip(exchange=exchange, searchtext=symbol)
            optidx_or_optstk = "OPTIDX"
        print(ret)
        #logging.info(ret)
        #logging.info(f"Searching for scrip - {symbol} using Finvasia API ")
        if ret != None:
            symbols = ret["values"]
            for symbol_index in symbols:
                token = symbol_index["token"]

        ret = self.api.searchscrip(exchange="NFO", searchtext=symbol)
        print(ret)
        #logging.info(ret)
        if ret != None:
            symbols = ret["values"]
            for symbol_idx in symbols:
                if symbol_idx["instname"] == "OPTSTK" or symbol_idx["instname"] == "OPTIDX":
                    if symbol_idx["dname"].split(" ")[3] == "CE":
                        if symb_one_strike == 0:
                            symb_one_strike = int(float(symbol_idx["dname"].split(" ")[2]))
                            # continue
                        else:
                            symb_two_strike = int(symbol_idx["dname"].split(" ")[2])
                            break
        strike_diff = abs(symb_one_strike - symb_two_strike)

        return token, strike_diff
        # print('{0} token is {1}'.format(symbol['tsym'], symbol['token']))

#buy nifty call option and buy banknifty put options or vice-versa, that is buy nifty put option and buy banknifty call option
    def options_long_nifty_short_banknifty_or_reverse(self,symbol, option_type_nifty,option_type_banknifty):
        global optidx_or_optstk
        is_hedged = True
        go_ahead=True

        if option_type_nifty == option_type_banknifty:
            is_hedged=False
        
        call_symbol, call_ltp_price,call_atm_token_lotsize, call_sym,call_strike = self.get_itm_strike_price_symbol(
            symbol, option_type_nifty
        )

        put_symbol, pe_buy_symbol, put_strike, put_ltp_price,go_ahead = self.get_closest_ltp_symbols_with_retry((call_ltp_price) , symbol, option_type_banknifty, "BANKNIFTY",call_symbol)
            
        print("After get_closest_ltp_symbols call")
        print(put_symbol)
        print(pe_buy_symbol)
        print(put_strike)
        print(put_ltp_price)


        """ Place orders only if there is a go-ahead"""
        if go_ahead:

            ''' logging.info("Before Place_orders call -Sell ")
            logging.info(f"buy_sym - {call_symbol}")
            logging.info(f"strike - {call_strike}")
            logging.info(f"ltp_price - {call_ltp_price}") '''
            strategy_id = str(generate_unique_number())+"_" +optidx_or_optstk
            self.place_orders("B",
                call_symbol,
                "",
                call_strike,
                call_strike,
                atm_expiry,
                atm_expiry,
                symbol,
            1,
                call_atm_token_lotsize * int(lots_multiplier),
                float(call_ltp_price),
                float(call_ltp_price),
                strategy_id,is_hedged
            )

            ''' logging.info("Before Place_orders call - sell ")
            logging.info("ce_buy_symbol - %s",put_symbol)
            logging.info("sell_strike - %s",str(put_strike))
            logging.info("sell_price - %s",str(put_ltp_price)) '''
            self.place_orders("B",
                put_symbol,
                "",
                put_strike,
                put_strike,
                atm_expiry,
                atm_expiry,
                symbol,
                1,
                15 * int(lots_multiplier),# 15-is the banknifty quantity,TODO:Remove the hardcoding for the same
                float(put_ltp_price),
                float(put_ltp_price),
                strategy_id,is_hedged
            )
        else:
            print(
                "either strike or price or option Type is not correct. Hence orders not placed"
        )

    def options_short_straddle(self,symbol, option_type):
        global optidx_or_optstk
        go_ahead=True
        call_symbol, call_ltp_price,call_atm_token_lotsize, call_sym,call_strike = self.get_itm_strike_price_symbol(
            symbol, option_type
        )

        '''Calculate put ltp ,find the symbol and put strike etc'''
        ''' reversed_input = call_symbol[::-1]
        put_symbol_rev = reversed_input.replace("C","P",1)
        put_symbol = put_symbol_rev[::-1]


        ret_val = api.searchscrip("NFO", put_symbol)

        if ret_val != None:
            symbols = ret_val["values"]
            for symbol_loop in symbols:
                # print('{0} token is {1}'.format(symbol['tsym'], symbol['token']))
                atm_token = symbol_loop["token"]
                atm_token_lotsize = int(symbol_loop["ls"])

        ret_quote = api.get_quotes(exchange="NFO", token=atm_token)
        put_ltp_price = ret_quote["lp"]
        put_strike = call_strike '''


        put_symbol, pe_sell_symbol, put_strike, put_ltp_price,go_ahead = self.get_closest_ltp_symbols_with_retry((call_ltp_price) , symbol, "P", call_sym,call_symbol)
            
        print("After get_closest_ltp_symbols call")
        print(put_symbol)
        print(pe_sell_symbol)
        print(put_strike)
        print(put_ltp_price)


        #go_ahead = True  # check_price_strike_optiontype(For_token,ce_buy_symbol,strike,sell_strike,atm_expiry,atm_expiry,symbol,1,atm_token_lotsize,float(ltp_price),float(sell_price))
        """ Place orders only if there is a go-ahead"""
        if go_ahead:

            ''' logging.info("Before Place_orders call -Sell ")
            logging.info(f"buy_sym - {call_symbol}")
            logging.info(f"strike - {call_strike}")
            logging.info(f"ltp_price - {call_ltp_price}") '''
            strategy_id = str(generate_unique_number())+"_" +optidx_or_optstk
            self.place_orders("S",
                call_symbol,
                "",
                call_strike,
                call_strike,
                atm_expiry,
                atm_expiry,
                symbol,
                1,
                call_atm_token_lotsize * int(lots_multiplier),
                float(call_ltp_price),
                float(call_ltp_price),
                strategy_id,True
            )

            ''' logging.info("Before Place_orders call - sell ")
            logging.info("ce_buy_symbol - %s",put_symbol)
            logging.info("sell_strike - %s",str(put_strike))
            logging.info("sell_price - %s",str(put_ltp_price)) '''
            self.place_orders("S",
                put_symbol,
                "",
                put_strike,
                put_strike,
                atm_expiry,
                atm_expiry,
                symbol,
                1,
                call_atm_token_lotsize * int(lots_multiplier),
                float(put_ltp_price),
                float(put_ltp_price),
                strategy_id,True
            )
        print(
            "either strike or price or option Type is not correct. Hence order not placed"
        )

    def options_buy_index_stock(self,symbol, option_type,buy_or_sell):

        global optidx_or_optstk
        go_ahead=True
        call_symbol, call_ltp_price,call_atm_token_lotsize, call_sym,call_strike = self.get_itm_strike_price_symbol(
            symbol, option_type
        )
        strategy_id=str(generate_unique_number())+"_"+optidx_or_optstk
        if go_ahead:
        
            ''' logging.info("Before Place_orders call -Sell ")
            logging.info("buy_sym - %s",call_symbol)
            logging.info("strike - %s",str(call_strike))
            logging.info("ltp_price - %s",str(call_ltp_price)) '''

            self.place_orders(buy_or_sell,
                call_symbol,
                "",
                call_strike,
                call_strike,
                atm_expiry,
                atm_expiry,
                symbol,
                1,
                call_atm_token_lotsize * int(lots_multiplier),
                float(call_ltp_price),
                float(call_ltp_price),
                strategy_id,False
            )

    def options_Buy_ATM_Call_Sell_Deep_OTM_Calls(self,symbol, option_type):
        buy_sym, ltp_price, atm_token_lotsize, sym,_ = self.get_itm_strike_price_symbol(
            symbol, option_type
        )
        global optidx_or_optstk
        ce_buy_symbol, ce_sell_symbol, sell_strike, sell_price,go_ahead = self.get_closest_ltp_symbols_with_retry((ltp_price) / 2, symbol, option_type, sym,buy_sym)
        
        #go_ahead = True  # check_price_strike_optiontype(For_token,ce_buy_symbol,strike,sell_strike,atm_expiry,atm_expiry,symbol,1,atm_token_lotsize,float(ltp_price),float(sell_price))
        """ Place orders only if there is a go-ahead"""
        if go_ahead:
            
            ''' logging.info("Before Place_orders call -Buy ")
            logging.info("buy_sym - %s",buy_sym)
            logging.info("strike - %s",str(strike))
            logging.info("ltp_price - %s",str(ltp_price)) '''
            strategy_id = str(generate_unique_number())+"_" +optidx_or_optstk
            self.place_orders("B",
                buy_sym,
                ce_buy_symbol,
                strike,
                sell_strike,
                atm_expiry,
                atm_expiry,
                symbol,
                1,
                atm_token_lotsize * int(lots_multiplier),
                float(ltp_price),
                float(sell_price),
                strategy_id,True
            )

            ''' logging.info("Before Place_orders call - sell ")
            logging.info("ce_buy_symbol - %s",ce_buy_symbol)
            logging.info("sell_strike - %s",str(sell_strike))
            logging.info("sell_price - %s",str(sell_price)) '''
            self.place_orders("S",
                ce_buy_symbol,
                "",
                sell_strike,
                sell_strike,
                atm_expiry,
                atm_expiry,
                symbol,
                1,
                atm_token_lotsize * int(lots_multiplier) * 2,
                float(sell_price),
                float(sell_price),
                strategy_id,True
            )
        print(
            "either strike or price or option Type is not correct. Hence order not placed"
        )    
#def options_Buy_ATM_Calls_Sell_DeepITM_Call(symbol,option_type,strategy_enum_value):
    
    def options_Buy_ATM_Calls_Sell_DeepITM_Call(self,symbol, option_type):
        buy_sym, ltp_price, atm_token_lotsize, sym,_ = self.get_itm_strike_price_symbol(
            symbol, option_type
        )
        global optidx_or_optstk

        ce_buy_symbol, ce_sell_symbol, sell_strike, sell_price,go_ahead = self.get_closest_ltp_symbols_with_retry((ltp_price) * 2, symbol, option_type, sym,buy_sym)
            
        #go_ahead = True  # check_price_strike_optiontype(For_token,ce_buy_symbol,strike,sell_strike,atm_expiry,atm_expiry,symbol,1,atm_token_lotsize,float(ltp_price),float(sell_price))
        """ Place orders only if there is a go-ahead"""
        if go_ahead:
            ''' logging.info("Before Place_orders call -Buy ")
            logging.info(f"buy_sym - {buy_sym}")
            logging.info(f"strike - {strike}")
            logging.info(f"ltp_price - {ltp_price}") '''
            strategy_id = str(generate_unique_number())+"_" +optidx_or_optstk
            self.place_orders("B",
                buy_sym,
                ce_buy_symbol,
                strike,
                sell_strike,
                atm_expiry,
                atm_expiry,
                symbol,
                1,
                atm_token_lotsize * int(lots_multiplier) * 2,
                float(ltp_price),
                float(sell_price),
                strategy_id,True
            )
            ''' logging.info("Before Place_orders call - sell ")
            logging.info("ce_buy_symbol - %s",ce_buy_symbol)
            logging.info("sell_strike - %s",str(sell_strike))
            logging.info("sell_price - %s",str(sell_price)) '''
            
            self.place_orders("S",
                ce_buy_symbol,
                "",
                sell_strike,
                sell_strike,
                atm_expiry,
                atm_expiry,
                symbol,
                1,
                atm_token_lotsize * int(lots_multiplier),
                float(sell_price),
                float(sell_price),
                strategy_id,True
            )
        print(
            "either strike or price or option Type is not correct. Hence order not placed"
        )

    def get_itm_strike_price_symbol(self,symbol, option_type):
        global pe_tsym
        global ce_tsym
        global put_price
        global call_price
        global atm_strike
        global atm_expiry
        global atm_token
        global strike
        logging.info(f" 1. Inside get_itm_strike_price_symbol for  - {symbol} - Option type - {option_type}")
        exch = symbol.split(":")[0]
        sym_to_search = symbol.split(":")[1]
        
        spot_tok, strike_diff = self.get_token_from_symbol(exch, sym_to_search)
        atm_expiry_dates = self.get_expiry_dates("NFO", sym_to_search)
        if atm_expiry_dates == None:
            print(f"exiting as the expiry date for the symbol - {sym_to_search} could not be found")
            return
        else:
            atm_expiry = atm_expiry_dates[1]
        print("ATM Expiry-", atm_expiry)

        logging.info(f" 2. ATM Expiry- {atm_expiry}")

        ret = self.api.get_quotes(exchange="NSE", token=spot_tok)
        if ret is None:
            print(f"exiting as the get quotes for the symbol - {sym_to_search} with -  {spot_tok } could not be found")
            return
        
        ltp = ret.get("lp")
        atm_ltp = float(ltp)
        ltp_str = str(float(ltp))
        sym = ret.get("symname")
        TYPE = option_type

        if strike_diff > 0:
            strike = int(round(float(ltp) / float(strike_diff), 0) * float(strike_diff))
        else:
            strike = int(round(float(ltp) / 100, 0) * 100)

        print("Buy strike - ", strike)
        logging.info(" 3. Buy strike - {str(strike}")

        ce_buy_trading_symbol = sym + atm_expiry + TYPE + str(strike)
        print("Spot price of - ", symbol + " is - ", ltp_str)
        logging.info("Spot price of - {symbol} is - {str(ltp_str)}")
        ret_val = self.api.searchscrip("NFO", ce_buy_trading_symbol)

        if ret_val != None:
            symbols = ret_val["values"]
            for symbol_loop in symbols:
                # print('{0} token is {1}'.format(symbol['tsym'], symbol['token']))
                atm_token = symbol_loop["token"]
                atm_token_lotsize = int(symbol_loop["ls"])

        ret_quote = self.api.get_quotes(exchange="NFO", token=atm_token)
        ltp_price = ret_quote["lp"]
        optionchain = self.api.get_option_chain("NFO", ce_buy_trading_symbol, strike, 12)
        optionchainsym = optionchain["values"]
        for Symbol in optionchainsym:
            (Symbol["token"])

        token = [Symbol["token"] for Symbol in optionchainsym]

        #modified_tokens = [26000,26013]
        modified_tokens=[]
        for Symbol in optionchainsym:
            token = Symbol["token"]
            modified_token = "NFO|" + token
            modified_tokens.append(modified_token)

        modified_tokens.append("NSE|" + spot_tok)
        spot_tokens.append(spot_tok)
        print(modified_tokens)

        lock.acquire()
        socket_rt_df = self.api.subscribe(modified_tokens)
        socket_rt_df = pd.DataFrame.from_dict(
            feedJson, orient="index", columns=["ltp", "Tsym", "openi", "pdopeni"]
        )
        print(socket_rt_df)
        lock.release()
        #logging.info(socket_rt_df)

        return ce_buy_trading_symbol, float(ltp_price), atm_token_lotsize, sym,strike

    def check_price_strike_optiontype(self,
        token,
        ce_buy_symbol,
        Strike,
        sell_strike,
        atm_expiry,
        symbol,
        atm_token_lotsize,
        ltp_price,
        sell_price,
    ):
        pass

    def place_orders(self,
    buy_or_sell,
    option_trading_symbol,
    ce_sell_trading_symbol,
    ce_buy_strike,
    ce_sell_strike,
    ce_buy_expiry,
    ce_sell_expiry,
    symbol,
    lot_multiple,
    lot_size,
    trade_price,
    sell_price,
    strategy_id,
    is_hedged
):
   
        B_or_S = "BUY" if (buy_or_sell  == "B") else "SELL"
        try:
            trading_quantity = lot_multiple * lot_size 
            ##placing orders*************************************************
            trade_order = self.api.place_order(
                buy_or_sell= B_or_S,
                product_type="M",
                exchange="NFO",
                tradingsymbol=option_trading_symbol,
                quantity=trading_quantity,
                discloseqty=0,
                price_type="MKT",
                price=trade_price,
                trigger_price=None,
                retention="DAY",
                remarks="ce_order_buy_001"
            )

            if trade_order:
                ce_order_buy_id = trade_order["norenordno"]
                
                stockitem_ord = stockitem(
                    option_trading_symbol,
                    trade_order["norenordno"],
                    trade_price,
                    trading_quantity,
                    B_or_S,
                    False,
                    False,
                    0.0,
                    B_or_S,
                    ce_buy_strike,
                    ce_buy_expiry,
                    strategy_id,
                    is_hedged
                )
                self.insertordersexecuted(stockitem_ord)
                #logging.info(f"Order placed successfully, option_trading_symbol = {option_trading_symbol}")

                return ce_order_buy_id
            else:
                return None
        except Exception as e:
            logging.info("Order placement failed: ")# , e.message)

    def retry_with_backoff(self,fn, retries = 5, backoff_in_seconds = 1):
        x = 0
        while True:
            try:
                return fn()
            except:
                if x == retries:
                    raise

            sleep = (backoff_in_seconds * 2 ** x + 
                    random.uniform(0, 1))
            time.sleep(sleep)
            x += 1

    def insertordersexecuted(self,stockitm):
        orders = []
        try:
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
                    "StrategyId":stockitm.strategy_id,
                    "IsHedged":stockitm.is_hedged
                }
            )
            if repository_setting == "1":
                file_repo = json_file_repository()
                data = file_repo.add_record(orders[0])
            else:
                x = client[databasename][collectionname].insert_many(orders[0])
        except Exception as e:
            logging.info(e.message)
            # try to start the mongodb service 
            stop_service('MongoDB')
            sleep(5)
            start_service('MongoDB')
            sleep(10)

    def insert_orders_into_Mongodb(self):
        pass

    def get_expiry_dates(self,exchange, symbol):
        import re
        import datetime

        sd = self.api.searchscrip(exchange, symbol)

        if sd is None: #and sd['stat'] == "Not_ok":
            return None
        
        if sd['stat'] == "Ok":
            sd = sd["values"]
            tsym_values = [Symbol["tsym"] for Symbol in sd]
            dates = [re.search(r"\d+[A-Z]{3}\d+", tsym).group() for tsym in tsym_values]
            dates = [date for date in dates if len(date) == 7]
            formatted_dates = [
                datetime.datetime.strptime(date, "%d%b%y").strftime("%Y-%m-%d")
                for date in dates
            ]
            sorted_formatted_dates = sorted(formatted_dates)
            sorted_dates = [
                datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d%b%y").upper()
                for date in sorted_formatted_dates
            ]
            expiry_dates = sorted_dates
            return expiry_dates
        else:
            return None

    def contains_substring_after_numerics(self,input_string, substring):
        # Reverse both the input string and the substring
        reversed_input = input_string[::-1]
        reversed_substring = substring[::-1]
        count=0
        # Initialize a flag to track if numeric characters are encountered
        numeric_found = False

        # Iterate through the reversed input string
        for char in reversed_input:
            if char.isdigit() or char == '.':
                numeric_found = True
            elif numeric_found:
                # Check if the reversed substring appears after numerics
                if reversed_substring[0] == reversed_input[count]:
                    return True
                else:
                    return False
            count = count+1
        return False

    def get_closest_ltp_symbols_with_retry(self,ltp_value, symbol, opt_type, sym_to_filter_on,call_symbol):

        option_strike_counter=0
        go_ahead=True

        while option_strike_counter <=10:
            put_symbol, pe_sell_symbol, put_strike, put_ltp_price = (
                self.get_closest_ltp_symbols((ltp_value) , symbol, opt_type, sym_to_filter_on,call_symbol)
            )
            if put_symbol != "":
                break
            option_strike_counter += 1 
            sleep(10)
        if option_strike_counter >10:
            go_ahead = False
        return put_symbol, pe_sell_symbol, put_strike, put_ltp_price,go_ahead

    def get_closest_ltp_symbols(self,ltp_value, symbol, opt_type, sym_to_filter_on,call_symbol):
        closest_symbols_c = ""
        closest_symbols_p = ""
        sell_strike = 0
        sell_price = 0
        sym_to_filter_on = str(sym_to_filter_on).upper()
        lock.acquire()
        if feedJson:
            socket_rt_df = pd.DataFrame.from_dict(
                feedJson, orient="index", columns=["ltp", "Tsym", "openi", "pdopeni"]
            )
            #include only symbols we are looking for for example 'NIFTY','BANKNIFTY','FINNIFTY','MIDCPNIFTY' etc and exclude the call symbol
            # that was found in the earlier steps
            df_sym = socket_rt_df[socket_rt_df["Tsym"].str.contains(sym_to_filter_on)]

            # socket_rt_df.to_csv('dataframe_Nifty.csv')
            df_sym["diff"] = abs(df_sym["ltp"] - ltp_value)
            #str reversed_str = [::-1]
            regex_pattern = rf'{opt_type}'
            #regex_pattern  = rf'/^[a-zA-Z][a-zA-Z0-9]*[{opt_type}]\d+$/'


            df_c = df_sym[df_sym["Tsym"].str.contains(regex_pattern, case=False)]
            #df['has_option_type'] = df['options'].str.contains(regex_pattern, case=False)

            
            
            if not df_c.empty:
            #if not df_sym.empty:
                min_diff_c = df_c["diff"].min()
                closest_symbols_c = df_c[df_c["diff"] == min_diff_c]["Tsym"].values[0]
                sell_strike = closest_symbols_c.split(opt_type)[-1]
                sell_price = df_c[df_c["diff"] == min_diff_c]["ltp"].values[0]
                print("Sell Strike - ")
                print(sell_strike)
                print("Closest strike Symbol - ")
                print(closest_symbols_c)
                print("Sell Price - ")
                print(sell_price)
        lock.acquire()
        return closest_symbols_c, closest_symbols_p, sell_strike, sell_price

    def check_sl_pt(self):
        import datetime
        mtmlossprofit = 0.0
        listoftrades = None
        trading_price = 0.0
        listoftrades = get_traded_records(collectionname, True)

        for index, row in listoftrades.iterrows():
            # first update the Last Traded Price from real-time stock market
            lock.acquire()
            trading_price = float(row["Ltp"])
            df_Tsym = socket_rt_df[row["TradingSymbol"] == self.socket_rt_df["Tsym"]]
            if not df_Tsym.empty:
                trading_price = self.socket_rt_df[row["TradingSymbol"] == self.socket_rt_df["Tsym"]]["ltp"].values[0]
            else:
                ret = self.api.searchscrip(exchange="NFO", searchtext=row["TradingSymbol"])
                if ret: 
                    ret_quote = self.api.get_quotes(exchange="NFO", token=ret['values'][0]['token'])
                if ret_quote and  ret_quote['stat'] == 'Ok':
                    trading_price = ret_quote["lp"]
            lock.release()      
            trading_price = float(trading_price)
            if row["IsHedged"] == True:
                update_trades(row["OrderId"], "FinalPrice",trading_price)
                update_trades(row["OrderId"], "FinalTradedDate",datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
                continue
            ''' if row["SlHit"] == True or row["TpHit"] == True:
                mtmlossprofit = mtmlossprofit + (
                    row["Ltp"] * row["Qty"] - trading_price * row["Qty"]
                )
                continue
            else:
                update_trades(row["OrderId"], "FinalPrice",trading_price) '''

            if row["SlHit"] == False and row["TpHit"] == False:
                
                tradingsymbol = row["TradingSymbol"]
                sl_val = 0.0
                tp_val = 0.0
                traded_price = row["Ltp"]
                sl_val,tp_val = get_sl_tp_values(row["StrategyId"],row["Ltp"],row["OrderType"])
                ''' if row["OrderType"] == "SELL" or row["OrderType"]  == "S" :
                    sl_val = traded_price + traded_price * 0.1   #0.35
                    tp_val = traded_price - traded_price * 0.2   # 0.7
                else:
                    sl_val = traded_price - traded_price * 0.1   # 0.35
                    tp_val = traded_price + traded_price * 0.2   # 0.7   '''
            
                update_trades(row["OrderId"], "FinalPrice",trading_price)
                update_trades(row["OrderId"], "FinalTradedDate",datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

                if row["OrderType"] == "SELL" or row["OrderType"]  == "S":
                    if trading_price <= tp_val or trading_price >= sl_val:
                        if trading_price <= tp_val:
                            update_trades(row["OrderId"], "TpHit",True)
                        else:
                            update_trades(row["OrderId"], "SlHit",True)
                else:
                    if trading_price >= tp_val or trading_price <= sl_val:
                        if trading_price >= tp_val:
                            update_trades(row["OrderId"], "TpHit",True)
                        else:
                            update_trades(row["OrderId"], "SlHit",True)

            print("ID-" + str(row["OrderId"]) + "  " + "Trading Symbol - " + row["TradingSymbol"])

        print("The      MTM   amount ==" + str(mtmlossprofit))

    def calculate_mtm_buy_2_sell_1(self):
        pass

    def calculate_mtm(self):
        import pandas as pd

        coll = client[databasename][collectionname]
        listoftrades = get_traded_records(collectionname, True) #pd.DataFrame(list(coll.find({})))

        if listoftrades is not None and not listoftrades.empty:
            listoftrades = listoftrades[
                ["BANKNIFTY" in x for x in listoftrades["TradingSymbol"]]
            ]
            listoftrades["FinalValue"] = listoftrades["FinalPrice"] * listoftrades["Qty"]
            listoftrades["LtpValue"] = listoftrades["Ltp"] * listoftrades["Qty"]

            mtm = 0.0
            capitaldeployed = 0.0
            totallossamount = 0.0
            totalprofitamount = 0.0
            trading_price = 0.0
            for index, row in listoftrades.iterrows():
                row["Mtm"] = 0.0
                # only consider sell calls and sell puts for now
                if row["ProductType"] == "sell" or row["ProductType"] == "intradaysell":

                    if row["TpHit"] == True:
                        row["Mtm"] = int(row["LtpValue"]) - int(row["FinalValue"])
                    elif row["SlHit"] == True:
                        row["Mtm"] = int(row["LtpValue"]) - int(row["FinalValue"])
                    else:
                        lock.acquire()
                        df_Tsym = socket_rt_df[row["TradingSymbol"] == socket_rt_df["Tsym"]]
                        if not df_Tsym.empty:
                            trading_price = socket_rt_df[row["TradingSymbol"] == socket_rt_df["Tsym"]][
                                "ltp"
                            ].values[0]
                        
                        else:
                            trading_price = 0
                        # trading_price = socket_rt_df[row['TradingSymbol']==socket_rt_df['Tsym']]['ltp'].values[0]
                        trading_price = float(trading_price)
                        row["Mtm"] = int(row["Ltp"] * row["Qty"]) - int(
                            trading_price * row["Qty"]
                        )
                        lock.release()

                mtm = mtm + row["Mtm"]
                if row["SlHit"] == False and row["TpHit"] == False:
                    capitaldeployed = capitaldeployed + row["LtpValue"]
                if row["SlHit"] == True and row["TpHit"] == False:
                    totallossamount = totallossamount + row["Mtm"]
                if row["SlHit"] == False and row["TpHit"] == True:
                    totalprofitamount = totalprofitamount + row["Mtm"]
            print("Final MTM - Loss or Gain for the day#####")
            logging.info("Final MTM - Loss or Gain for the day#####")
            mtmvalue = mtm  # *25.0
            print("*****" + str(mtmvalue) + "*****")
            logging.info("*****" + str(mtmvalue) + "*****")

            print("Capital deployed for the above MTM - ")
            logging.info("Capital deployed for the above MTM - ")
            print(str(capitaldeployed))
            logging.info(str(capitaldeployed))
            print("Total stop loss amount for the day till now - ")
            logging.info("Total stop loss amount for the day till now - ")
            print(str(totallossamount))
            logging.info(str(totallossamount))
            print("Total Profit amount for the day till now - - ")
            logging.info("Total Profit amount for the day till now - - ")
            print(str(totalprofitamount))
            logging.info(str(totalprofitamount))

            return listoftrades

    def append_latest_socket_data(self,token):
        # Initialize a dictionary to store candlestick data for each token
        candlestick_data_dict = {}

        # Initialize variables for storing LTP values over 60 seconds
        ltp_values_dict = {}

        # Shared start time for all tokens
        start_time_dict = {}

        # List of tokens
        tokens = ["38030", "4", "1"]  # Add more tokens as needed

        # Initialize data structures for each token
        for token in tokens:
            candlestick_data_dict[token] = pd.DataFrame(
                columns=["timestamp", "open", "high", "low", "close"]
            )
            ltp_values_dict[token] = []
            start_time_dict[token] = self.get_next_minute_start()

        while True:
            for token in tokens:
                # Simulating live data stream (replace this with your actual data retrieval logic)
                # For simplicity, we are using a random value as LTP.
                ltp = float(df(token))
                ltp_values_dict[token].append(ltp)

                # Check if 60 seconds have passed for the specific token
                if datetime.datetime.now() >= start_time_dict[token] + datetime.timedelta(
                    seconds=60
                ):
                    # Calculate OHLC values
                    open_price = ltp_values_dict[token][0]
                    high_price = max(ltp_values_dict[token])
                    low_price = min(ltp_values_dict[token])
                    close_price = ltp_values_dict[token][-1]

                    # Print OHLC values and current time
                    print(
                        f"{self.format_time(start_time_dict[token])} - Token: {token}, Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}"
                    )

                    # Create a new row of data
                    new_data = pd.DataFrame(
                        {
                            "timestamp": [start_time_dict[token]],
                            "open": [open_price],
                            "high": [high_price],
                            "low": [low_price],
                            "close": [close_price],
                        }
                    )

                    # Concatenate the new data with the existing candlestick_data for the token
                    candlestick_data_dict[token] = pd.concat(
                        [candlestick_data_dict[token], new_data], ignore_index=True
                    )

                    # Clear the list for the next 60 seconds
                    ltp_values_dict[token] = []

                    # Update start time for the next 60-second interval for the specific token
                    start_time_dict[token] = self.get_next_minute_start()

            # Wait for the next iteration
            time.sleep(0.5)

    # Function to get the next minute's start time
    def get_next_minute_start(self):

        now = datetime.datetime.now()
        next_minute_start = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, 0)
        if (now.second >= 59):  # Adjust the starting point based on your requirement (e.g., start from the current minute if second is 30 or more)
            next_minute_start += datetime.timedelta(minutes=1)
        return next_minute_start
    # Function to format time in HH:MM:SS
    def format_time(self,current_time):
        return current_time.strftime("%H:%M:%S")

    def convert_to_ohlc_create_file(self):
        from copy import deepcopy

        global_lock = True
        lock.acquire()
        # token_list=['26000','26009']
        starttime = datetime.now().strftime("%H_%M_%S")
        candlestick_data_dict_dup = {}
        if candlestick_data_dict is not None:
            candlestick_data_dict_dup = candlestick_data_dict.copy()
            socket_rt_df = pd.DataFrame.from_dict(
                {
                    (i, j): candlestick_data_dict_dup[i][j]
                    for i in candlestick_data_dict_dup.keys()
                    for j in candlestick_data_dict_dup[i].keys()
                },
                orient="index",
            )
            # resample_LTP = data['LTP'].resample('15Min').ohlc(_method='ohlc')
            formattedfilepath = CreateCsvFile("Consolidated_OHLC", starttime, True)
            socket_rt_df.to_csv(formattedfilepath)
            for idx, data in socket_rt_df.groupby(level=0):
                # if idx in token_list:
                df_level_zero = socket_rt_df.xs(idx, level=0)
                df_level_zero["tt"] = pd.to_datetime(df_level_zero["tt"])
                df_level_zero = df_level_zero.set_index("tt")
                df_level_zero["Volume"] = df_level_zero["Volume"].astype(int)
                df_level_zero = df_level_zero.resample("1min").apply(self.agg_ohlcv)
                df_level_zero = df_level_zero.ffill()
                print(df_level_zero)
                formattedfilepath = CreateCsvFile(idx, starttime, True)
                df_level_zero.to_csv(formattedfilepath)
        global_lock = False
        lock.release()

    def agg_ohlcv(self,x):
        arr = x["ltp"].values
        names = {
            "low": min(arr) if len(arr) > 0 else np.nan,
            "high": max(arr) if len(arr) > 0 else np.nan,
            "open": arr[0] if len(arr) > 0 else np.nan,
            "close": arr[-1] if len(arr) > 0 else np.nan,
            "Volume": sum(x["Volume"].values) if len(x["Volume"].values) > 0 else 0,
        }
        return pd.Series(names)

    def pipe_no_wait_execute_trade(self):
        import struct

        print("waiting for client")
        win32pipe.ConnectNamedPipe(pipe, None)
        print("got client")

        request_len = win32file.ReadFile(pipe, 4)
        request_len = struct.unpack("I", request_len[1])[0]
        request_data = win32file.ReadFile(pipe, request_len)

        # convert to bytes
        input = str(request_data[1], "UTF-8")
        print(input.split(",")[0])
        print(input.split(",")[1])
        print(str(request_data[1], "UTF-8"))
        response_data = "Order Placed".encode(ENCODING)
        response_len = struct.pack("I", len(response_data))
        win32file.WriteFile(pipe, response_len)
        win32file.WriteFile(pipe, response_data)

    def update_trade_prices(self):
        
        ''' socket_rt_df = pd.DataFrame.from_dict(
                feedJson, orient="index", columns=["ltp", "Tsym", "openi", "pdopeni"]
            ) '''
        time.sleep(5)
        while True:
            time.sleep(2)
            #lock.acquire()
            ''' socket_rt_df = pd.DataFrame.from_dict(
                feedJson, orient="index", columns=["ltp", "Tsym", "openi", "pdopeni"]
            )
            print(socket_rt_df) '''
            self.check_sl_pt()
            self.calculate_mtm()
            #lock.release()

    def process_messages(self,queue):
        while True:
            message = self.trading_message_queue.get()  # Block until a message is available
            if message == "STOP":
                break  # Exit the loop when the sentinel value is received
            # Process the message (e.g., append it to a list)
            p56=message
            args = str.split(message,',')
            if args[0] == '1':
                self.options_buy_index_stock(args[1],args[2],args[3])
            print(f"Received message: {message}")
    def post_messages(self,message):

        self.trading_message_queue.put(message)

if __name__ == "__main__":
    try:
        logging.info("**********************************************************")
        #init()
        #setupWebSocket()
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('Nifty')
        # get_token_from_symbol('NSE:OFSS')
        # get_token_from_symbol('NSE:OFSS')
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:Nifty','P',MultiLegStrategy.2_Calls_Buy_ATM_and_1_Call_Sell_Deep_ITM.value)
        #options_Buy_ATM_Calls_Sell_DeepITM_Call("NSE:Nifty", "P")
        #options_Buy_ATM_Calls_Sell_DeepITM_Call("NSE:Nifty", "P")
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('MCX:CRUDEOILM16FEB24','C')
        #options_Buy_ATM_Calls_Sell_DeepITM_Call("NSE:Nifty Bank", "C")
        #options_Buy_ATM_Calls_Sell_DeepITM_Call("NSE:Nifty Bank", "C")
        #options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:Nifty Bank','C')
        #options_Buy_ATM_Call_Sell_Deep_OTM_Calls('NSE:TATAMOTORS','P')
        #options_Buy_ATM_Call_Sell_Deep_OTM_Calls('NSE:TATAMOTORS','C')
        #options_short_straddle('NSE:GODREJCP','C')
        #options_short_straddle('NSE:Nifty Bank','C')
        #options_short_straddle('NSE:VOLTAS','P')
        #options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:HCLTECH','P')
        #options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:BPCL','C')
        
        #options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:AUBANK','C')

        fth = finvasia_trading_helper()
        #fth.options_buy_index_stock("NSE:Nifty Bank","C","B")
        #fth.options_buy_index_stock("NSE:Nifty", "P","B")
        
        #options_long_nifty_short_banknifty_or_reverse("NSE:Nifty", "P","C") 

        #options_buy_index_stock("NSE:Nifty", "C","B")
        #options_buy_index_stock("NSE:Nifty", "C","B")
        
        #options_buy_index_stock("NSE:Nifty Bank","P","B")
        #options_buy_index_stock("NSE:Nifty Bank","P","B")
        #options_buy_index_stock('NSE:LUPIN',"P","B")
        #options_buy_index_stock('NSE:IGL',"P","B")
        #options_buy_index_stock('NSE:Nifty Bank','C')
        #options_buy_index_stock('NSE:TATAMOTORS','P',"B")
        #options_buy_index_stock('NSE:BPCL','C',"B")
        #options_buy_index_stock("NSE:GODREJCP","C","B")
        #options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:HDFCAMC','P')
        #options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:LALPATHLAB','P')
        #options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:DABUR','P')
        #options_Buy_ATM_Call_Sell_Deep_OTM_Calls('NSE:GODREJPROPS','P')
        #options_Buy_ATM_Call_Sell_Deep_OTM_Calls('NSE:GODREJPROPS','P')
        #options_Buy_ATM_Call_Sell_Deep_OTM_Calls('NSE:DLF','C')
        #schedule.every(1).minutes.do(check_sl_pt)
        #schedule.every(1).minutes.do(calculate_mtm)
        #schedule.every().day.at("10:30").do(convert_to_ohlc_create_file)
        #schedule.every().day.at("12:30").do(convert_to_ohlc_create_file)
        #schedule.every().day.at("15:30").do(convert_to_ohlc_create_file)


        ''' my_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=process_messages, args=(my_queue,))
        process.start()

        # Add messages to the queue (e.g., from the main process)
        my_queue.put(("1","NSE:Nifty","P","C"))
        #my_queue.put("World")
        #my_queue.put("STOP")  # Use a sentinel value to stop the process '''


        ''' thread_process = threading.Thread(target=fth.process_messages, args=(fth.trading_message_queue,))
        thread_process.daemon = True
        thread_process.start() '''
        
        fth.post_messages("1,NSE:Nifty,C,B")
        while True:
            time.sleep(2)
            if time.localtime == "":
                break

        ''' while True:
                #schedule.run_pending()
            time.sleep(2)
            lock.acquire()
            fth.socket_rt_df = pd.DataFrame.from_dict(
                feedJson, orient="index", columns=["ltp", "Tsym", "openi", "pdopeni"]
            )
            print(fth.socket_rt_df)
            fth.check_sl_pt()
            fth.calculate_mtm()
            lock.release() '''
        
            # pipe_no_wait_execute_trade()
        #process.join()  # Wait for the process to finish
        fth.thread_process.join()
        fth.thread_update.join()
    except KeyboardInterrupt:
        logging.info("Logged out of the program using keyboard interrupt....")
