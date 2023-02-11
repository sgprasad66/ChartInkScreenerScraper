# Schedule Library imported
import schedule
import time
import pymongo

from kite_trade import *
global client
global kite
global listoftrades
# Functions setup

def initialize():
    print("scheduled_squareoff_positions.py started.......")
    import pandas as pd
    import certifi

    global client
    global kite
    
    client = pymongo.MongoClient("mongodb+srv://TradingUser:Akshara66*@cluster0.tosvjw6.mongodb.net/?retryWrites=true&w=majority",tlsCAFile=certifi.where())
    enctoken =  "ORKPV7HB46RCDV9q5NYwLibZ6cXpAWJgMikbMZuGYdb4EQAR+kJqoh9o9mWwRTQmRFnwzRUwX99X08SNBb7MlHjXLAOZESU5KXzdtyT8ECmBUGsywbMGFA=="
    kite = KiteApp(enctoken=enctoken)


def calculate_mtm():

    import pandas as pd
    coll = client["ChartInkTradeLog"]["10_02_2023"]
    listoftrades = pd.DataFrame(list(coll.find({})))

    listoftrades['FinalValue'] = listoftrades['FinalPrice']*listoftrades['Qty']
    listoftrades['LtpValue'] = listoftrades['Ltp']*listoftrades['Qty']

    mtm=0.0
    for index,row in listoftrades.iterrows():
        if  (row['ProductType'] == 'buy' or row['ProductType'] == 'intradaybuy') :
            #if (row['SlHit'] == True):
                row['Mtm'] = row['FinalValue']-row['LtpValue']
            #else:
            #    row['Mtm'] = row['FinalValue']-row['LtpValue']

        else:
            #if (row['SlHit'] == True):
                row['Mtm'] = row['LtpValue']-row['FinalValue']
            #else:
            #    row['Mtm'] = row['LtpValue']-row['FinalValue']

        print(str(row['Mtm']))
        mtm= mtm+row['Mtm']

    #listoftrades['FinalValue'] = listoftrades['FinalPrice']*listoftrades['Qty']
    print("Final MTM - Loss or Gain for the day#####")
    print(str(mtm))
    print(listoftrades)


def check_sl_pt():
    global listoftrades
    print("Inside check_sl_pt of scheduled_squareoff_positions.py.........")
    import pymongo

    import datetime
    import pandas as pd

    global client
    global kite

    coll = client["ChartInkTradeLog"]["10_02_2023"]
    listoftrades = pd.DataFrame(list(coll.find({})))

    print(listoftrades.head(5))
    mtmlossprofit=0.0
    for index,row in listoftrades.iterrows():
        if row['SlHit'] == False and row['TpHit'] == False:
            tradingsymbol = "NSE:"+row['TradingSymbol']
            sl_val=0.0
            tp_val=0.0
            trading_price=0.0
            current_price = row['FinalPrice']  #kite.ltp(tradingsymbol)[tradingsymbol]['last_price']
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
                    coll.update_one({"_id":row['_id']},{"$set":{"FinalPrice":current_price}})
                    if current_price <= tp_val:
                        coll.update_one({"_id":row['_id']},{"$set":{"TpHit":True}})
                        mtmlossprofit = mtmlossprofit+(traded_price*row['Qty']-current_price*row['Qty'])
                    else:
                        coll.update_one({"_id":row['_id']},{"$set":{"SlHit":True}})
                        mtmlossprofit = mtmlossprofit+(current_price*row['Qty']-traded_price*row['Qty'])

            else:
                if current_price >= tp_val or current_price <= sl_val:
                    producttype=None
                    if row['ProductType'] == 'buy' :
                        productype = kite.PRODUCT_CNC
                    else:
                        productype = kite.PRODUCT_MIS
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
                    coll.update_one({"_id":row['_id']},{"$set":{"FinalPrice":current_price}})
                    if current_price <= sl_val:
                        coll.update_one({"_id":row['_id']},{"$set":{"SlHit": True}})
                        mtmlossprofit = mtmlossprofit+(traded_price*row['Qty']- current_price*row['Qty'])
                    else:
                        coll.update_one({"_id":row['_id']},{"$set":{"TpHit": True}})
                        mtmlossprofit = mtmlossprofit+ (current_price*row['Qty']-traded_price*row['Qty'])
                        
        print("ID-"+str(row['_id']) +"  " +"Trading Symbol - "+ row['TradingSymbol'])

    print("MTM===================%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%---------------"+str(mtmlossprofit))

    print("Get ready for Stop loss and Profit Taking loop")
    
# Task scheduling
# After every 10mins geeks() is called.
#schedule.every(2).minutes.do(check_sl_pt)

# Loop so that the scheduling task
# keeps on running all time.
#while True:
    #initialize()
	# Checks whether a scheduled task
	# is pending to run or not
    #schedule.run_pending()
    #time.sleep(1)

if __name__ == "__main__":    
    initialize()
    check_sl_pt()
    calculate_mtm()


