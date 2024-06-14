from time import sleep
import time
from datetime import datetime, timedelta
import pandas as pd
from ChartInk_Scaper_FileWatcher_Processor import stockitem
import helper
import pymongo
import certifi
from NorenRestApiPy.NorenApi import NorenApi
from datetime import datetime
import datetime as dt
import time
import pyotp
import schedule
import logging
import numpy as np
from chartink_through_python import CreateCsvFile
import win32pipe, win32file, pywintypes
from Utils import MultiLegStrategy

# IPC parameters
PIPE_NAME = r"\\.\pipe\simple-ipc-pipe"
ENCODING = "ascii"


pipe = win32pipe.CreateNamedPipe(
    PIPE_NAME,
    win32pipe.PIPE_ACCESS_DUPLEX,
    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE,
    1,
    65536,
    65536,
    0,
    None,
)

pd.set_option("display.max_rows", None)

config = helper.read_config()
mongodbclient = config["MongoDBSettings"]["mongodbclient"]
databasename = config["MongoDBSettings"]["databasename"]
collectionname = config["MongoDBSettings"]["collectionname"]
deletecollectionname = config["MongoDBSettings"]["deletecollectionname"]
feed_opened = False
socket_opened = False
feedJson = {}
candlestick_data_dict = {}
global_lock = False
spot_tokens = []


# client = pymongo.MongoClient(mongodbclient,tlsCAFile=certifi.where())
client = pymongo.MongoClient(mongodbclient, ssl=False)

#########Rabbit-MQ start  -#########

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

import pika, json

# from main import Product, db

params = pika.URLParameters(
    "amqp://endnpqyd:lFusCAGdoGWor8Ro6RffeopDcZambQ05@albatross.rmq.cloudamqp.com/endnpqyd"
)

connection = pika.BlockingConnection(params)

channel = connection.channel()

channel.queue_declare(queue="main")

#########Rabbit-MQ end  -###########


class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(
            self,
            host="https://api.shoonya.com/NorenWClientTP/",
            websocket="wss://api.shoonya.com/NorenWSTP/",
        )


api = ShoonyaApiPy()


def init():

    user = "FA136660"
    pwd = "Sgprasad12@"
    vc = "FA136660_U"
    app_key = "acf591571dae1737ac28495698e2eaf1"
    token = "54F7Y5B2H5N32W36TYFOJUD6W67U2W4V"
    global fno_scrips
    time.sleep(2)
    while True:
        try:
            factor2 = pyotp.TOTP(token).now()
            ret = api.login(
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


def event_handler_feed_update(tick_data):
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


def event_handler_order_update(order_update):
    pass  # print(f"order feed {order_update}")


def open_callback():
    global feed_opened
    feed_opened = True
    print("Websocket opened")


def setupWebSocket():
    global feed_opened
    print("waiting for socket opening")
    api.start_websocket(
        order_update_callback=event_handler_order_update,
        subscribe_callback=event_handler_feed_update,
        socket_open_callback=open_callback,
    )
    while feed_opened == False:
        pass


init()
setupWebSocket()


def get_token_from_symbol(exchange, symbol):
    symb_one_strike = 0
    symb_two_strike = 0
    strike_diff = 0
    token = 0

    ret = api.searchscrip(exchange=exchange, searchtext=symbol)

    print(ret)
    logging.info(ret)

    if ret != None:
        symbols = ret["values"]
        for symbol_index in symbols:
            token = symbol_index["token"]

    ret = api.searchscrip(exchange="NFO", searchtext=symbol)
    print(ret)
    logging.info(ret)
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


# def options_Buy_ATM_Calls_Sell_DeepITM_Call(symbol,option_type,strategy_enum_value):
def options_Buy_ATM_Calls_Sell_DeepITM_Call(symbol, option_type):

    buy_sym, ltp_price, atm_token_lotsize, sym = get_itm_strike_price_symbol(
        symbol, option_type
    )

    while True:
        ce_buy_symbol, ce_sell_symbol, sell_strike, sell_price = (
            get_closest_ltp_symbols((ltp_price) * 2, symbol, option_type, sym)
        )
        if ce_buy_symbol != "":
            break
        sleep(10)
    print("After get_closest_ltp_symbols call")
    print(ce_buy_symbol)
    print(ce_sell_symbol)
    print(sell_strike)
    print(sell_price)

    go_ahead = True  # check_price_strike_optiontype(For_token,ce_buy_symbol,strike,sell_strike,atm_expiry,atm_expiry,symbol,1,atm_token_lotsize,float(ltp_price),float(sell_price))
    """ there is no go-ahead to place orders"""
    if go_ahead:
        place_orders(
            buy_sym,
            ce_buy_symbol,
            strike,
            sell_strike,
            atm_expiry,
            atm_expiry,
            symbol,
            1,
            atm_token_lotsize,
            float(ltp_price),
            float(sell_price),
        )
    print(
        "either strike or price or option Type is not correct. Hence order not placed"
    )


def get_itm_strike_price_symbol(symbol, option_type):
    global pe_tsym
    global ce_tsym
    global put_price
    global call_price
    global atm_strike
    global atm_expiry
    global atm_token
    global strike

    exch = symbol.split(":")[0]
    sym_to_search = symbol.split(":")[1]

    spot_tok, strike_diff = get_token_from_symbol(exch, sym_to_search)
    atm_expiry = get_expiry_dates("NFO", sym_to_search)[1]
    # atm_expiry = get_expiry_dates('MCX', 'CRUDEOILM16FEB24')[0]
    print("ATM Expiry-", atm_expiry)

    ret = api.get_quotes(exchange="NSE", token=spot_tok)
    # ret = api.get_quotes(exchange='MCX', token=tok)

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
    ce_buy_trading_symbol = sym + atm_expiry + TYPE + str(strike)
    print("Spot price of - ", symbol + " is - ", ltp_str)
    ret_val = api.searchscrip("NFO", ce_buy_trading_symbol)

    if ret_val != None:
        symbols = ret_val["values"]
        for symbol_loop in symbols:
            # print('{0} token is {1}'.format(symbol['tsym'], symbol['token']))
            atm_token = symbol_loop["token"]
            atm_token_lotsize = int(symbol_loop["ls"])

    ret_quote = api.get_quotes(exchange="NFO", token=atm_token)
    ltp_price = ret_quote["lp"]
    optionchain = api.get_option_chain("NFO", ce_buy_trading_symbol, strike, 12)
    optionchainsym = optionchain["values"]
    for Symbol in optionchainsym:
        (Symbol["token"])

    token = [Symbol["token"] for Symbol in optionchainsym]

    modified_tokens = []
    for Symbol in optionchainsym:
        token = Symbol["token"]
        modified_token = "NFO|" + token
        modified_tokens.append(modified_token)

    modified_tokens.append("NSE|" + spot_tok)
    spot_tokens.append(spot_tok)
    print(modified_tokens)

    df = api.subscribe(modified_tokens)
    df = pd.DataFrame.from_dict(
        feedJson, orient="index", columns=["ltp", "Tsym", "openi", "pdopeni"]
    )
    print(df)

    return ce_buy_trading_symbol, float(ltp_price), atm_token_lotsize, sym


def check_price_strike_optiontype(
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


def place_orders(
    ce_buy_trading_symbol,
    ce_sell_trading_symbol,
    ce_buy_strike,
    ce_sell_strike,
    ce_buy_expiry,
    ce_sell_expiry,
    symbol,
    lot_multiple,
    lot_size,
    buy_price,
    sell_price,
):
    """if symbol == 'Nifty':
        quantity_ce_buy = lot_multiple *lot_size*2
        quantity_ce_sell = lot_multiple *lot_size
    else:
        quantity_ce_buy = lot_multiple *lot_size*2
        quantity_ce_sell = lot_multiple *lot_size"""

    quantity_ce_buy = lot_multiple * lot_size * 2
    quantity_ce_sell = lot_multiple * lot_size
    ##placing orders*************************************************
    ce_order = api.place_order(
        buy_or_sell="B",
        product_type="M",
        exchange="NFO",
        tradingsymbol=ce_buy_trading_symbol,
        quantity=quantity_ce_buy,
        discloseqty=0,
        price_type="MKT",
        price=buy_price,
        trigger_price=None,
        retention="DAY",
        remarks="ce_order_buy_001",
    )

    pe_order = api.place_order(
        buy_or_sell="S",
        product_type="M",
        exchange="NFO",
        tradingsymbol=ce_sell_trading_symbol,
        quantity=quantity_ce_sell,
        discloseqty=0,
        price_type="MKT",
        price=sell_price,
        trigger_price=None,
        retention="DAY",
        remarks="ce_order_sell_001",
    )
    ce_order_buy_id = ce_order["norenordno"]
    pe_order_sell_id = pe_order["norenordno"]

    stockitembullish = stockitem(
        ce_buy_trading_symbol,
        ce_order,
        buy_price,
        quantity_ce_buy,
        "BUY",
        False,
        False,
        0.0,
        "buy",
        ce_buy_strike,
        ce_buy_expiry,
    )
    stockitembearish = stockitem(
        ce_sell_trading_symbol,
        pe_order,
        sell_price,
        quantity_ce_sell,
        "SELL",
        False,
        False,
        0.0,
        "sell",
        ce_sell_strike,
        ce_sell_expiry,
    )

    insertordersexecuted(stockitembullish)
    insertordersexecuted(stockitembearish)

    return (ce_order_buy_id, pe_order_sell_id)


def insertordersexecuted(stockitm):
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


def insert_orders_into_Mongodb():
    pass


def get_expiry_dates(exchange, symbol):
    import re
    import datetime

    sd = api.searchscrip(exchange, symbol)
    sd = sd["values"]
    tsym_values = [Symbol["tsym"] for Symbol in sd]
    dates = [re.search(r"\d+[A-Z]{3}\d+", tsym).group() for tsym in tsym_values]
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


def get_closest_ltp_symbols(ltp_value, symbol, opt_type, sym_to_filter_on):
    closest_symbols_c = ""
    closest_symbols_p = ""
    sell_strike = 0
    sell_price = 0
    sym_to_filter_on = str(sym_to_filter_on).upper()
    if feedJson:
        df = pd.DataFrame.from_dict(
            feedJson, orient="index", columns=["ltp", "Tsym", "openi", "pdopeni"]
        )
        # df = df.filter(like=spot_token, axis=0)
        # df[df['Tsym'].str.contains('NIFTY^')]
        df_sym = df[df["Tsym"].str.contains(sym_to_filter_on)]
        # df.to_csv('dataframe_Nifty.csv')
        df_sym["diff"] = abs(df_sym["ltp"] - ltp_value)
        df_c = df_sym[df_sym["Tsym"].str.contains(opt_type)]
        if not df_c.empty:
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
    return closest_symbols_c, closest_symbols_p, sell_strike, sell_price


def get_traded_records(tradeddate, is_cumulative):
    # global listoftrades
    print("Inside get_traded_records of Alice_Blue_API.py.........")
    import pandas as pd

    listoftrades = pd.DataFrame()

    coll = client[databasename][tradeddate]
    listoftrades = pd.DataFrame(list(coll.find({})))

    return listoftrades


def check_sl_pt():
    import datetime

    mtmlossprofit = 0.0
    listoftrades = None
    coll = client[databasename][collectionname]
    trading_price = 0.0

    listoftrades = get_traded_records(collectionname, True)
    for index, row in listoftrades.iterrows():
        # first update the Last Traded Price from real-time stock market

        df_Tsym = df[row["TradingSymbol"] == df["Tsym"]]
        if not df_Tsym.empty:
            trading_price = df[row["TradingSymbol"] == df["Tsym"]]["ltp"].values[0]
        else:
            trading_price = 0
        trading_price = float(trading_price)
        if row["SlHit"] == True or row["TpHit"] == True:
            mtmlossprofit = mtmlossprofit + (
                row["Ltp"] * row["Qty"] - trading_price * row["Qty"]
            )
            continue
        else:
            coll.update_one(
                {"_id": row["_id"]}, {"$set": {"FinalPrice": trading_price}}
            )

        if row["SlHit"] == False and row["TpHit"] == False:
            tradingsymbol = row["TradingSymbol"]
            sl_val = 0.0
            tp_val = 0.0
            traded_price = row["Ltp"]

            if row["OrderType"] == "SELL":
                sl_val = traded_price + traded_price * 0.1
                tp_val = traded_price - traded_price * 0.3
            else:
                sl_val = traded_price - traded_price * 0.1
                tp_val = traded_price + traded_price * 0.3

            if row["OrderType"] == "SELL":
                if trading_price <= tp_val or trading_price >= sl_val:
                    # for kite order placement uncomment below

                    coll.update_one(
                        {"_id": row["_id"]}, {"$set": {"FinalPrice": trading_price}}
                    )
                    coll.update_one(
                        {"_id": row["_id"]},
                        {"$set": {"FinalTradedDate": datetime.datetime.now()}},
                    )
                    if trading_price <= tp_val:
                        coll.update_one({"_id": row["_id"]}, {"$set": {"TpHit": True}})
                    else:
                        coll.update_one({"_id": row["_id"]}, {"$set": {"SlHit": True}})
            else:
                if trading_price >= tp_val or trading_price <= sl_val:
                    # for kite order placement uncomment below

                    coll.update_one(
                        {"_id": row["_id"]}, {"$set": {"FinalPrice": trading_price}}
                    )
                    coll.update_one(
                        {"_id": row["_id"]},
                        {"$set": {"FinalTradedDate": datetime.datetime.now()}},
                    )
                    if trading_price >= tp_val:
                        coll.update_one({"_id": row["_id"]}, {"$set": {"TpHit": True}})
                    else:
                        coll.update_one({"_id": row["_id"]}, {"$set": {"SlHit": True}})

        print(
            "ID-" + str(row["_id"]) + "  " + "Trading Symbol - " + row["TradingSymbol"]
        )

    print("The      MTM   amount ==" + str(mtmlossprofit))


def calculate_mtm_buy_2_sell_1():
    pass


def calculate_mtm():
    import pandas as pd

    coll = client[databasename][collectionname]
    listoftrades = pd.DataFrame(list(coll.find({})))

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
                    df_Tsym = df[row["TradingSymbol"] == df["Tsym"]]
                    if not df_Tsym.empty:
                        trading_price = df[row["TradingSymbol"] == df["Tsym"]][
                            "ltp"
                        ].values[0]
                    else:
                        trading_price = 0
                    # trading_price = df[row['TradingSymbol']==df['Tsym']]['ltp'].values[0]
                    trading_price = float(trading_price)
                    row["Mtm"] = int(row["Ltp"] * row["Qty"]) - int(
                        trading_price * row["Qty"]
                    )

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


def append_latest_socket_data(token):
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
        start_time_dict[token] = get_next_minute_start()

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
                    f"{format_time(start_time_dict[token])} - Token: {token}, Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}"
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
                start_time_dict[token] = get_next_minute_start()

        # Wait for the next iteration
        time.sleep(0.5)


# Function to get the next minute's start time
def get_next_minute_start():
    now = datetime.datetime.now()
    next_minute_start = datetime.datetime(
        now.year, now.month, now.day, now.hour, now.minute, 0
    )
    if (
        now.second >= 59
    ):  # Adjust the starting point based on your requirement (e.g., start from the current minute if second is 30 or more)
        next_minute_start += datetime.timedelta(minutes=1)
    return next_minute_start


# Function to format time in HH:MM:SS
def format_time(current_time):
    return current_time.strftime("%H:%M:%S")


global candlestick_data
candlestick_data = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close"])


def convert_to_ohlc_create_file():
    from copy import deepcopy

    global_lock = True

    # token_list=['26000','26009']
    starttime = datetime.now().strftime("%H_%M_%S")
    candlestick_data_dict_dup = {}
    if candlestick_data_dict is not None:
        candlestick_data_dict_dup = candlestick_data_dict.copy()
        df = pd.DataFrame.from_dict(
            {
                (i, j): candlestick_data_dict_dup[i][j]
                for i in candlestick_data_dict_dup.keys()
                for j in candlestick_data_dict_dup[i].keys()
            },
            orient="index",
        )
        # resample_LTP = data['LTP'].resample('15Min').ohlc(_method='ohlc')
        formattedfilepath = CreateCsvFile("Consolidated_OHLC", starttime, True)
        df.to_csv(formattedfilepath)
        for idx, data in df.groupby(level=0):
            # if idx in token_list:
            df_level_zero = df.xs(idx, level=0)
            df_level_zero["tt"] = pd.to_datetime(df_level_zero["tt"])
            df_level_zero = df_level_zero.set_index("tt")
            df_level_zero["Volume"] = df_level_zero["Volume"].astype(int)
            df_level_zero = df_level_zero.resample("1min").apply(agg_ohlcv)
            df_level_zero = df_level_zero.ffill()
            print(df_level_zero)
            formattedfilepath = CreateCsvFile(idx, starttime, True)
            df_level_zero.to_csv(formattedfilepath)
    global_lock = False


def agg_ohlcv(x):
    arr = x["ltp"].values
    names = {
        "low": min(arr) if len(arr) > 0 else np.nan,
        "high": max(arr) if len(arr) > 0 else np.nan,
        "open": arr[0] if len(arr) > 0 else np.nan,
        "close": arr[-1] if len(arr) > 0 else np.nan,
        "Volume": sum(x["Volume"].values) if len(x["Volume"].values) > 0 else 0,
    }
    return pd.Series(names)


def pipe_no_wait_execute_trade():
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


class stock_info:
    def __init__(self, sym, opttype):
        self.Symbol = sym
        self.OptionType = opttype


def callback(ch, method, properties, body):
    print("Received in main")
    str_body = body.decode()
    data = json.loads(str_body)
    strlist = data.split("|")

    print(data)
    options_Buy_ATM_Calls_Sell_DeepITM_Call(strlist[1], strlist[2])


if __name__ == "__main__":
    try:
        logging.info("**********************************************************")
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('Nifty')
        # get_token_from_symbol('NSE:OFSS')
        # get_token_from_symbol('NSE:OFSS')
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:Nifty','P',MultiLegStrategy.2_Calls_Buy_ATM_and_1_Call_Sell_Deep_ITM.value)
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:Nifty','C')
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:Nifty','P')
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('MCX:CRUDEOILM16FEB24','C')
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:Nifty Bank','P')
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:Nifty Bank','C')
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:Nifty Bank','P')
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:TATASTEEL','C')
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:HINDALCO','C')
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:BANKBARODA','P')
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:UPL','P')
        # options_Buy_ATM_Calls_Sell_DeepITM_Call('NSE:ONGC','P')
        schedule.every(1).minutes.do(check_sl_pt)
        schedule.every(1).minutes.do(calculate_mtm)
        schedule.every().day.at("10:30").do(convert_to_ohlc_create_file)
        schedule.every().day.at("12:30").do(convert_to_ohlc_create_file)
        schedule.every().day.at("15:30").do(convert_to_ohlc_create_file)
        channel.basic_consume(queue="main", on_message_callback=callback, auto_ack=True)

        print("Started Consuming")

        channel.start_consuming()

        while True:
            schedule.run_pending()
            time.sleep(2)
            df = pd.DataFrame.from_dict(
                feedJson, orient="index", columns=["ltp", "Tsym", "openi", "pdopeni"]
            )
            print(df)
            # pipe_no_wait_execute_trade()

    except KeyboardInterrupt:
        logging.info("Logged out of the program using keyboard interrupt....")
    channel.close()
