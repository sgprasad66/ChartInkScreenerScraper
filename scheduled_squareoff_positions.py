# Schedule Library imported
import schedule
import time
import pymongo

from kite_trade import *
global client
global kite
global listoftrades
# Functions setup

import helper

config = helper.read_config()

mongodbclient = config['MongoDBSettings']['mongodbclient']
databasename = config['MongoDBSettings']['databasename']
collectionname = config['MongoDBSettings']['collectionname']
deletecollectionname=config['MongoDBSettings']['deletecollectionname']
enctoken=config['KiteSettings']['enctoken']

def initialize():
    print("scheduled_squareoff_positions.py started.......")
    import pandas as pd
    import certifi

    global client
    global kite
    
    client = pymongo.MongoClient(mongodbclient,tlsCAFile=certifi.where())
    #enctoken =  "AF5py89+I7oOsT2cXsIuSPLNpXYCuJzaQ6LMwElxZm5T2xmVIWeICoCeSj4Cf/4Baoge0LxFEUPNaohA3nFFW3xKvF+TePjUR/Aqpwn9tb/Rkten3DwlPA=="
    kite = KiteApp(enctoken=enctoken)

def updateslhitcolumn():
    import pandas as pd
    coll = client[databasename][deletecollectionname]
    listoftrades = pd.DataFrame(list(coll.find({})))

    for index,row in listoftrades.iterrows():

        coll.update_one({"_id":row['_id']},{"$set":{"TpHit":False}})

def calculate_mtm():

    import pandas as pd
    coll = client[databasename][deletecollectionname]
    listoftrades = pd.DataFrame(list(coll.find({})))

    if listoftrades is not None:
        listoftrades['FinalValue'] = listoftrades['FinalPrice']*listoftrades['Qty']
        listoftrades['LtpValue'] = listoftrades['Ltp']*listoftrades['Qty']

        mtm=0.0
        capitaldeployed=0.0
        totallossamount=0.0
        totalprofitamount=0.0
        for index,row in listoftrades.iterrows():
            if  (row['ProductType'] == 'buy' or row['ProductType'] == 'intradaybuy') :
                if row['TpHit'] == True:
                    row['Mtm'] = int(row['FinalValue'])-int(row['LtpValue'])
                elif row['SlHit'] == True:
                    row['Mtm'] = int(row['LtpValue'])-int(row['FinalValue'])
                else:
                    row['Mtm'] =0.0

            else:
                if row['TpHit'] == True:
                    row['Mtm'] = int(row['LtpValue'])-int(row['FinalValue'])
                elif row['SlHit'] == True:
                    row['Mtm'] = int(row['LtpValue'])-int(row['FinalValue'])
                else:
                    row['Mtm'] =0.0

            print(str(row['Mtm']))
            mtm= mtm+row['Mtm']
            if row['SlHit'] == False and row['TpHit'] == False:
                capitaldeployed = capitaldeployed+row['LtpValue']
            if row['SlHit'] == True and row['TpHit'] == False:
                totallossamount=totallossamount+row['Mtm']
            if row['SlHit'] == False and row['TpHit'] == True:
                totalprofitamount=totalprofitamount+row['Mtm']
        print("Final MTM - Loss or Gain for the day#####")
        print(f" Stock - {row['TradingSymbol']} - Last Trading Price - {row['LtpValue']} - Final Price  {row['FinalPrice']} -- Qty  - {row['Qty']} -  MTM - {row['Mtm']}")
        print("Capital deployed for the above MTM - ")
        print(str(capitaldeployed))
        print("Total stop loss amount for the day till now - ")
        print(str(totallossamount))
        print("Total Profit amount for the day till now - - ")
        print(str(totalprofitamount))
        print(listoftrades)


def check_sl_pt():
    global listoftrades
    print("Inside check_sl_pt of scheduled_squareoff_positions.py.........")
    import pymongo

    import datetime
    import pandas as pd

    global client
    global kite

    coll = client[databasename][deletecollectionname]
    listoftrades = pd.DataFrame(list(coll.find({})))

    print(listoftrades.head(5))
    mtmlossprofit=0.0
    for index,row in listoftrades.iterrows():
        if row['SlHit'] == False and row['TpHit'] == False:
            #tradingsymbol = "NSE:"+row['TradingSymbol']
            tradingsymbol = row['TradingSymbol']
            sl_val=0.0
            tp_val=0.0
            trading_price=0.0
            #current_price = row['FinalPrice'] 
            ltp = kite.ltp(tradingsymbol)
            if ltp != None and len(ltp) > 0:
                current_price = ltp[tradingsymbol]['last_price']
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
                                            tag="ChartInkScraper")
                        coll.update_one({"_id":row['_id']},{"$set":{"FinalPrice":current_price}})
                        coll.update_one({"_id":row['_id']},{"$set":{"FinalTradedDate":datetime.datetime.now()}})
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
                                            tag="ChartInkScraper")
                        coll.update_one({"_id":row['_id']},{"$set":{"FinalPrice":current_price}})
                        coll.update_one({"_id":row['_id']},{"$set":{"FinalTradedDate":datetime.datetime.now()}})
                        if current_price <= sl_val:
                            coll.update_one({"_id":row['_id']},{"$set":{"SlHit": True}})
                            mtmlossprofit = mtmlossprofit+(traded_price*row['Qty']- current_price*row['Qty'])
                        else:
                            coll.update_one({"_id":row['_id']},{"$set":{"TpHit": True}})
                            mtmlossprofit = mtmlossprofit+ (current_price*row['Qty']-traded_price*row['Qty'])
                coll.update_one({"_id":row['_id']},{"$set":{"FinalPrice":current_price}})
                        
        print("ID-"+str(row['_id']) +"  " +"Trading Symbol - "+ row['TradingSymbol'])

    print("The      MTM   amount =="+str(mtmlossprofit))

    print("Stop loss and Profit Taking loop")
    
# Task scheduling

schedule.every(1).minutes.do(check_sl_pt)
schedule.every(1).minutes.do(calculate_mtm)

# Loop so that the scheduling task
# keeps on running all time.
while True:
    initialize()
    #updateslhitcolumn()
    schedule.run_pending()
    time.sleep(1)

''' if __name__ == "__main__":    
    initialize()
    check_sl_pt()
    calculate_mtm() '''


