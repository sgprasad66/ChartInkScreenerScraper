import schedule
import time
import pymongo

from kite_trade import *
global client
global kite

def initialize():
    import pandas as pd
    import certifi
    global client

    client = pymongo.MongoClient("mongodb+srv://TradingUser:Akshara66*@cluster0.tosvjw6.mongodb.net/?retryWrites=true&w=majority",tlsCAFile=certifi.where())
    #enctoken = "zIHb6tJAjlPNKlWePko2v4RKCp8G9kKll4X5KTeGx16/xMjPb2pieapxQUxdmxZ8NaPiZhv3LQscrvFfpHb5wujmx3H+TNRW430TliWs/NHlwo10Vd+ywQ=="


def check_sl_pt():
    import pymongo

    import datetime
    import pandas as pd

    global client
    global kite
    enctoken =  "ORKPV7HB46RCDV9q5NYwLibZ6cXpAWJgMikbMZuGYdb4EQAR+kJqoh9o9mWwRTQmRFnwzRUwX99X08SNBb7MlHjXLAOZESU5KXzdtyT8ECmBUGsywbMGFA=="
    kite = KiteApp(enctoken=enctoken)

    listoftrades = pd.DataFrame(list(client["ChartInkTradeLog"]["_02_2023"].find({})))
    #listoxzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzftrades.l
    #print(listoftrades)
    print(listoftrades.head(5))
    for index,row in listoftrades.iterrows():
        #stockitem(row[])
        tradingsymbol = "NSE:"+row['TradingSymbol']
        sl_val=0.0
        tp_val=0.0
        trading_price=0.0
        current_price = kite.ltp(tradingsymbol)[tradingsymbol]['last_price']
        traded_price=row['Ltp']
        if row['OrderType'] == 'SELL':
            sl_val = (traded_price + traded_price*.01)
            tp_val = (traded_price - traded_price*.02)
        else:
            sl_val = (traded_price - traded_price*.01)
            tp_val = (traded_price + traded_price*.02)

        if row['OrderType'] == 'SELL':
            if current_price <= tp_val or current_price >= sl_val:
                order = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=row['TradingSymbol'],
                                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                                    quantity=row['Qty'],
                                    product=kite.PRODUCT_MIS,
                                    order_type=kite.ORDER_TYPE_MARKET,
                                    price=current_price,
                                    validity=None,
                                    disclosed_quantity=None,
                                    trigger_price=None,
                                    squareoff=None,
                                    stoploss=None,
                                    trailing_stoploss=None,
                                    tag="TradeViaPython")
        else:
            if current_price >= tp_val or current_price <= sl_val:
                producttype=None
                if row['ProductType'] == 'buy' :
                    productype = kite.PRODUCT_MIS
                else:
                    productype = kite.PRODUCT_CNC
                order = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=row['TradingSymbol'],
                                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                                    quantity=row['Qty'],
                                    product= productype,
                                    order_type=kite.ORDER_TYPE_MARKET,
                                    price=current_price,
                                    validity=None,
                                    disclosed_quantity=None,
                                    trigger_price=None,
                                    squareoff=None,
                                    stoploss=None,
                                    trailing_stoploss=None,
                                    tag="TradeViaPython")
        print(row['_id'])
        client["ChartInkTradeLog"]["09_02_2023"].update_one({"_id":row['_id']},{"$set":{"FinalPrice":current_price}})
        client["ChartInkTradeLog"]["09_02_2023"].update_one({"_id":row['_id']},{"$set":{"SlHit":'true'}})

    #result = client["ChartInkTradeLog"]["OrdersExecuted"].find({})
    #for i in result:
    #    print(i)
    print("Get ready for Stop loss and Profit Taking loop")

if __name__ == "__main__":
    initialize()
    check_sl_pt()
