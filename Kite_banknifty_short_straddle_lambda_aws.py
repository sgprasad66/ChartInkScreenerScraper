import json
import requests
import pandas as pd
from io import StringIO
import pymongo
from datetime import datetime as dt
from datetime import timedelta
import datetime
import time
from boto3 import client as boto3_client
from common import random_order_id

quote = "https://api.kite.trade/quote?i="
instruments = "https://api.kite.trade/instruments"
api_key = ""
access_token = ""
headers = {"X-Kite-Version" : "3", "Authorization" : f"token {api_key}:{access_token}"}
expiry_date = '2022-12-29'
index_symbol = 'BANKNIFTY22DECFUT'
sl_hit_thresold = 2
qty = 25

host = ""
client = pymongo.MongoClient(host)
db = client['test']

def get_data(query={}, project={"_id": 0}):
    data = db['tradelog'].find(query, project)
    return list(data)

def update_data(query, data):
    data.update({"modified_at": dt.now()})
    newvalues = { "$set": data }
    x = db['tradelog'].update_one(query, newvalues)

def insert_orders(orders):
    print(orders, "orders list")
    x = db['tradelog'].insert_many(orders)
    return x.inserted_ids

def find_entry():
    inst = requests.get(instruments + '/NFO', headers=headers).text
    df_fno = pd.read_csv(StringIO(inst))
    df_options = df_fno[df_fno.segment == 'NFO-OPT']

    df_bnf_only = df_options[(df_options.name.isin(['BANKNIFTY']))]
    df_bnf_only = df_bnf_only[['instrument_token', 'tradingsymbol', 'expiry', 'strike', 'instrument_type', 'name']]
    expiry_dates = df_bnf_only.expiry.unique()

    df = get_and_process_data(df_bnf_only, expiry_date)
    atm_strikes_with_type = get_atm_strikes(df['strike'], f"NFO:{index_symbol}")
    tradingsymbols = get_tradingsymbols(df, atm_strikes_with_type)
    return tradingsymbols

def get_quotes(symbols):
    res = requests.get(quote + symbols, headers=headers).json()
    df = pd.DataFrame(res['data'])
    df = df.T
    df1 = df['ohlc'].apply(pd.Series)
    df.drop(['depth', 'ohlc', 'last_quantity', 'lower_circuit_limit', 'upper_circuit_limit'], 1, inplace=True)
    df = pd.concat([df, df1], axis=1)
    return df

def get_and_process_data(df, exp):
    df_given_expiry = df[df.expiry == exp]
    niftyopt = list(map(str, df_given_expiry['instrument_token'].tolist()))
    nfo1 = '&i='.join(niftyopt[0:1000])
    df_with_quotes = get_quotes(nfo1)
    df = pd.merge(df, df_with_quotes, on='instrument_token')
    df.fillna(0)
    return df

def place_order(tradingsymbol, quantity, txn_type, order_type="MARKET", trigger_price=0):
    try:
        url = "https://api.kite.trade/orders/regular"

        payload = f"exchange=NFO&tradingsymbol={tradingsymbol}&transaction_type={txn_type}&order_type={order_type}&quantity={quantity}&price=0&product=MIS&validity=DAY&disclosed_quantity=0&trigger_price={trigger_price}&squareoff=0&stoploss=0&trailing_stoploss=0&variety=regular&user_id=UL4765"
        print(payload)

        response = requests.request("POST", url, headers=headers, data=payload)

        response = response.json()
        if not response["data"]:
            raise Exception()
        print(response, "responsee")
    except Exception as e:
        print(str(e))
        response = {"status": "success", "data": {"order_id": str(random_order_id())}}
        return response

def closest(lst, K):
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]

def get_ltp(symbol):
    url = f"https://api.kite.trade/quote/ltp?i={symbol}"
    response = requests.request("GET", url, headers=headers, data={}).json()
    ltp =  response["data"][symbol]["last_price"]
    return ltp

def get_atm_strikes(strike_list, symbol):
    """
        Gets the ATM+0.5% strike for CE and ATM-0.5% strike for PE
    """
    ltp = get_ltp(symbol)
    atm_strike_ce = closest(strike_list, ltp * 1.005) #ATM + 0.5% for CE
    atm_strike_pe = closest(strike_list, ltp * 0.995) #ATM + 0.5% for PE
    data = [
            {"strike_price": atm_strike_ce, "type": "CE"},
            {"strike_price": atm_strike_pe, "type": "PE"}
        ]
    return data

def get_tradingsymbols(df, strikes_with_type):
    """
        Gets tradingsymbol from strikes and types given i.e ce/pe
    """
    tradingsymbols = {}
    for leg in strikes_with_type:
        strike_price = leg['strike_price']
        inst_type = leg['type']
        tsymb_sr = df[(df['strike'] == strike_price) & (df['instrument_type'] == inst_type)]
        tradingsymbols[tsymb_sr['tradingsymbol'].values[0]] = inst_type
    return tradingsymbols

def get_ist_now():
    return dt.now() + timedelta(hours=5.5)

def exit_all_positions():
    print("Exiting all positions at after cut off time")
    sl_not_hit_by_3pm = get_data({"sl_hit": False}, {"order_id": 1, "tradingsymbol": 1, "qty": 1})

    for t in sl_not_hit_by_3pm:
        print(t['tradingsymbol'], t['qty'], "BUY")
        place_order(t['tradingsymbol'], t['qty'], "BUY")

def order_status(order_id):
    url = f"https://api.kite.trade/orders/{order_id}"
    payload={}

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()['data']['status'] #list of orders

def is_sl_hit(order_id):
    if order_id == "382270196720590":
        return True
    else:
        return False
    return order_status(order_id) == 'COMPLETE'

def track_sl(it):
    #Each leg SL Checking
    count_of_sl = len(get_data({"inst_type": it, "sl_hit": True}))

    if count_of_sl < sl_hit_thresold:
        sl_not_hit = get_data({"inst_type": it, "sl_hit": False}, {"order_id": 1})
        order_id = sl_not_hit[0]['order_id']
        
        if is_sl_hit(order_id):
            update_data({'order_id': order_id}, {'sl_hit': True})
            tradingsymbols = find_entry()
            if count_of_sl + 1 >= sl_hit_thresold:
                return
            for tradingsymbol, inst_type in tradingsymbols.items():
                if inst_type == it:
                    res = place_order(tradingsymbol, qty, "SELL")
                    ltp = get_ltp(f"NFO:{tradingsymbol}")
                    sl = ltp * 1.3
                    #Place SL-M order
                    order_obj = place_order(tradingsymbol, qty, "BUY", order_type='SL-M', trigger_price=sl)
                    order_id = order_obj['data']['order_id']
                    order = [{'inst_type': inst_type, 'tradingsymbol': tradingsymbol, 'qty': qty, 'order_id': order_id, 'sl': sl, 'sl_hit': False}]
                    insert_orders(order)


def lambda_handler(event, context):
    current_time = get_ist_now()
    
    if datetime.time(9, 19) < current_time.time() < datetime.time(15, 25):
        tradingsymbols = find_entry()
        orders = []
        sl_hit_count = 0
        no_of_trades = len(get_data({}))
        
        print(tradingsymbols)
        if no_of_trades == 0:
            for tradingsymbol, inst_type in tradingsymbols.items():
                res = place_order(tradingsymbol, qty, "SELL")
                ltp = get_ltp(f"NFO:{tradingsymbol}")
                sl = ltp * 1.3
                #Place SL-M order
                order_obj = place_order(tradingsymbol, qty, "BUY", order_type='SL-M', trigger_price=sl)
                order_id = order_obj['data']['order_id']
                orders.append({'inst_type': inst_type, 'tradingsymbol': tradingsymbol, 'qty': qty, 'order_id': order_id, 'sl': sl, 'sl_hit': False})
            insert_orders(orders)
        while True:
            track_sl("CE")
            track_sl("PE")

    elif current_time.time() > datetime.time(15, 0):
        exit_all_positions()