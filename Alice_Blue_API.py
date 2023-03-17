from pya3 import *
import logging
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta, TH
from kiteconnect import KiteConnect
import schedule
from kite_trade import *
from ChartInk_Scaper_FileWatcher_Processor import stockitem
import helper

global alice
config = helper.read_config()

mongodbclient = config['MongoDBSettings']['mongodbclient']
databasename = config['MongoDBSettings']['databasename']
collectionname = config['MongoDBSettings']['collectionname']
deletecollectionname=config['MongoDBSettings']['deletecollectionname']
enctoken=config['KiteSettings']['enctoken']
aliceblueusername=config['AliceBlueSettings']['username']
aliceblueapikey=config['AliceBlueSettings']['apikey']

log_filename_path =config['Logger']['LogFilePath']
log_file_Name=config['Logger']['LogFileName']

bnfshortstraddle_dict={'0930':None,'1030':None,'1130':None,'1230':None}

class bankniftystraddleitem:
    def __init__(self, inst_ce,ce_ltp,inst_pe,ltp_pe,):
        self.inst_ce = inst_ce
        self.ce_ltp= ce_ltp
        self.inst_pe = inst_pe
        self.ltp_pe =ltp_pe
        self.current_combinedpremium=0.0
        self.combpremiumatorderplacement=0.0
        self.current_ce_ltp=0.0
        self.current_pe_ltp=0.0
      

    def getcombinedpremium(self):
        self.combpremiumatorderplacement = self.ce_ltp+self.ltp_pe
        return self.combinedpremium    
    def getcurrentcombinedpremium(self):
        self.current_combinedpremium = self.current_ce_ltp+self.current_pe_ltp
        return self.current_combinedpremium

def get_kite():
    logging.basicConfig(filename=log_filename_path+'//'+log_file_Name,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=20)
    kiteObj = KiteApp(enctoken=enctoken)
    return kiteObj

def get_alice():
    global alice
    alice = Aliceblue(user_id=aliceblueusername,api_key=aliceblueapikey)
    print(alice.get_session_id())
    return alice

kite = get_kite()
instrumentsList = None
alice = get_alice()

def getCMP(tradingSymbol):
    quote = kite.quote(tradingSymbol)
    if quote:
        return quote[tradingSymbol]['last_price']
    else:
        return 0


def get_symbols(expiry, name, strike, ins_type):
    global instrumentsList
    instru=''
    if instrumentsList is None:
        instrumentsList = kite.instruments('NFO')

    lst_b = [num for num in instrumentsList if num['expiry'] == expiry and num['strike'] == strike
             and num['instrument_type'] == ins_type and num['name'] == name]
    if lst_b is not None and len(lst_b) != 0:
        instru = lst_b[0]['tradingsymbol']
    return instru


def place_order(tradingSymbol, price, qty, direction, exchangeType, product, orderType):
    try:
        orderId = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=exchangeType,
            tradingsymbol=tradingSymbol,
            transaction_type=direction,
            quantity=qty,
            price=price,
            product=product,
            order_type=orderType)

        logging.info('Order placed successfully, orderId = %s', orderId)
        return orderId
    except Exception as e:
        logging.info('Order placement failed: %s', e.message)

def place_order_aliceblue(i,q,b_or_s = "BUY"):
    global alice
    b_or_s = b_or_s.upper()
    try:
        od = alice.place_order(transaction_type = TransactionType.Sell if b_or_s == 'SELL' else TransactionType.Buy,
                        instrument = i,
                        quantity = q,
                        order_type = OrderType.Market,
                        product_type = ProductType.Intraday,
                        price = 0.0,
                        trigger_price = None,
                        stop_loss = None,
                        square_off = None,
                        trailing_sl = None,
                        is_amo = False,
                        order_tag='order1')
        logging.info('Order placed successfully, orderId = %s', od['NOrdNo'])
        return od['NOrdNo']
    except Exception as e:
        logging.info('Order placement failed: %s', e.message)
    
def insertordersexecuted(stockitm):
    import pymongo
    import certifi
    import datetime
    global client
    global orders
    global alice

    client = pymongo.MongoClient(mongodbclient,tlsCAFile=certifi.where())
    orders=[]

    orders.append({"TradingSymbol":stockitm.instrument_token,"OrderId":stockitm.order_id,"Qty":stockitm.quantity,"Ltp":stockitm.last_price,"OrderType":stockitm.ordertype,
                    "TpHit":stockitm.tp_hit,"SlHit":stockitm.sl_hit,"FinalPrice":stockitm.final_price,"ProductType":stockitm.producttype,"TradedDate":stockitm.traded_date,
                    "FinalTradedDate":stockitm.final_traded_date,"Strike":stockitm.strike,"Expiry":stockitm.expiry})
    
    x = client[databasename][collectionname].insert_many(orders)

def createshortstraddlebnf():
    # Find ATM Strike of Nifty
    #atm_strike = round(getCMP('NSE:NIFTY 50'), -2)
    global alice
    atm_strike = round(getCMP('NFO:BANKNIFTY23MARFUT'), -2)
    logging.info(f"At The Money strike ---{str(atm_strike)}")
    strike_ce=atm_strike-500
    logging.info(f"CE  strike ---{str(strike_ce)}")
    strike_pe = atm_strike+400
    logging.info(f"PE strike ---{str(strike_pe)}")

    next_thursday_expiry = datetime.today() + relativedelta(weekday=TH(1))

    ce = alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date=next_thursday_expiry.date().strftime("%Y-%m-%d"), is_fut=False,strike=strike_ce, is_CE=True)
    pe = alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date=next_thursday_expiry.date().strftime("%Y-%m-%d"), is_fut=False,strike=strike_pe, is_CE=False)

    symbol_ce = alice.get_scrip_info(ce)
    symbol_pe = alice.get_scrip_info(pe)

    ins = alice.get_instrument_by_symbol(symbol=symbol_ce['TSymbl'],exchange='NFO')

    ce_order = place_order_aliceblue(ins,25,'SELL')
    print(f"order for {symbol_ce['TSymbl']} - CE sell placed at {str(symbol_ce['LTP'])} ")
    logging.info(f"order for {symbol_ce['TSymbl']} - CE sell placed at {str(symbol_ce['LTP'])} ")
    stockitembullish = stockitem(symbol_ce['TSymbl'],ce_order,float(symbol_ce['LTP']),25,'SELL',False,False,0.0,'sell',strike_ce,next_thursday_expiry)   
    insertordersexecuted(stockitembullish)

    ins = alice.get_instrument_by_symbol(symbol=symbol_pe['TSymbl'],exchange='NFO')
    pe_order = place_order_aliceblue(ins,25,'SELL')

    print(f"order for {symbol_pe['TSymbl']} - PE sell placed at  {str(symbol_pe['LTP'])}")
    logging.info(f"order for {symbol_pe['TSymbl']} - PE sell placed at  {str(symbol_pe['LTP'])}")
    stockitembearish = stockitem(symbol_pe['TSymbl'],pe_order,float(symbol_pe['LTP']),25,'SELL',False,False,0.0,'sell',strike_pe,next_thursday_expiry)
    insertordersexecuted(stockitembearish)

def getlasttradedprice(strike,expiry,is_ce):

    global alice
    call=True
    if is_ce != 'CE':
        call= False

    next_thursday_expiry = datetime.today() + relativedelta(weekday=TH(1))
    ce = alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date=next_thursday_expiry.date().strftime("%Y-%m-%d"), is_fut=False,strike=strike, is_CE=call)
    symbol_ce = alice.get_scrip_info(ce)
    return symbol_ce['Ltp']

def updatecombinedpremiums():
    global alice

    for key,value in bnfshortstraddle_dict.items():
        if value is not None:
            symbol_ce = alice.get_scrip_info(value.inst_ce)
            symbol_pe = alice.get_scrip_info(value.inst_pe)
            checkslhit(symbol_ce,symbol_pe,key)
            logging.info("latest premium for {%s} - CE sell value now  - {%s} - placed at - {%s}",symbol_ce['TSymbl'],str(symbol_ce['LTP']),str(key))
            logging.info("latest premium for {%s} - PE sell value now - {%s} - placed at - {%s}",symbol_pe['TSymbl'],str(symbol_pe['LTP']),str(key))

def checkslhit(ce,pe,key):
    slprice=0.0
    item = bnfshortstraddle_dict(key)
    item.current_ce_ltp = float(ce['LTP'])
    item.current_pe_ltp = float(pe['LTP'])

    #for CE leg
    slprice = item.ce_ltp+item.ce_ltp*0.4
    if item.current_ce_ltp >= slprice:
        ins = alice.get_instrument_by_symbol(symbol=ce['TSymbl'],exchange='NFO')

        ce_order_sl = place_order_aliceblue(ins,25,'BUY')
        print(ce_order_sl)
        logging.info(ce_order_sl)
        print("Stop Loss Order for {%s} - CE sell placed at -{%s} ",ce['TSymbl'],str(ce['LTP']))
        logging.info(" Stop Loss Order for {%s} - CE sell placed at -{%s} ",ce['TSymbl'],str(ce['LTP']))

    #for pe leg stop loss order placement
    slprice = item.ltp_pe+item.ltp_pe*0.4
    if item.current_pe_ltp >= slprice:
        ins = alice.get_instrument_by_symbol(symbol=pe['TSymbl'],exchange='NFO')

        pe_order_sl = place_order_aliceblue(ins,25,'BUY')
        print(pe_order_sl)
        logging.info(pe_order_sl)
        print("Stop Loss Order for {%s} - PE sell placed at -{%s} ",pe['TSymbl'],str(pe['LTP']))
        logging.info(" Stop Loss Order for {%s} - PE sell placed at -{%s} ",pe['TSymbl'],str(pe['LTP']))

    #TODO:code to update the record to slhit=true in the mongodb database.
def calculate_mtm():
    import pandas as pd
    import pymongo
    import certifi
    client = pymongo.MongoClient(mongodbclient,tlsCAFile=certifi.where())

    coll = client[databasename][collectionname]
    querystring='{TradingSymbol:{"$regex": "BANKNIFTY"}}'
    listoftrades = pd.DataFrame(list(coll.find({}))) 
    if listoftrades is not None and not listoftrades.empty:
        listoftrades = listoftrades[['BANKNIFTY' in x for x in listoftrades['TradingSymbol']]]
        listoftrades['FinalValue'] = listoftrades['FinalPrice']*listoftrades['Qty']
        listoftrades['LtpValue'] = listoftrades['Ltp']*listoftrades['Qty']

        mtm=0.0
        capitaldeployed=0.0
        totallossamount=0.0
        totalprofitamount=0.0
        for index,row in listoftrades.iterrows():
            #only consider sell calls and sell puts for now
            if  (row['ProductType'] == 'sell' or row['ProductType'] == 'intradaysell') :
                if row['TpHit'] == True:
                    row['Mtm'] = int(row['LtpValue'])-int(row['FinalValue'])
                elif row['SlHit'] == True:
                    row['Mtm'] = int(row['LtpValue'])-int(row['FinalValue'])
                else:
                    row['Mtm'] =0.0
            ''' else:
                if row['TpHit'] == True:
                    row['Mtm'] = int(row['FinalValue'])-int(row['LtpValue'])
                elif row['SlHit'] == True:
                    row['Mtm'] = int(row['LtpValue'])-int(row['FinalValue'])
                else:
                    row['Mtm'] =0.0 '''

            str1 = f" Stock - {row['TradingSymbol']} - LTP - {row['Ltp']} - Final Price - {row['FinalPrice']}- LTPValue  - {row['LtpValue']} -FinalValue -  {row['FinalValue']} - Strike  -  {row['Strike']} --- MTM - {row['Mtm']}"
            print(str1)
            logging.info("Logging--"+str1)
            mtm= mtm+row['Mtm']
            if row['SlHit'] == False and row['TpHit'] == False:
                capitaldeployed = capitaldeployed+row['LtpValue']
            if row['SlHit'] == True and row['TpHit'] == False:
                totallossamount=totallossamount+row['Mtm']
            if row['SlHit'] == False and row['TpHit'] == True:
                totalprofitamount=totalprofitamount+row['Mtm']
        print("Final MTM - Loss or Gain for the day#####")
        logging.info("Final MTM - Loss or Gain for the day#####")
        print("*****"+str(mtm)+"*****")
        logging.info("*****"+str(mtm)+"*****")
        
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
        #print(listoftrades)
        #logging.log()


def check_sl_pt():
    global listoftrades
    print("Inside check_sl_pt of scheduled_squareoff_positions.py.........")
    import pandas as pd
    import datetime
    import pymongo
    import certifi
    client = pymongo.MongoClient(mongodbclient,tlsCAFile=certifi.where())
    mtmlossprofit=0.0

    coll = client[databasename][collectionname]
    querystring='{TradingSymbol:{"$regex": "BANKNIFTY"}}'
    listoftrades = pd.DataFrame(list(coll.find({}))) 

    if listoftrades is not None and not listoftrades.empty:
        listoftrades = listoftrades[['BANKNIFTY' in x for x in listoftrades['TradingSymbol']]]

        #print(listoftrades.head(5))
        
        for index,row in listoftrades.iterrows():
            if row['SlHit'] == False and row['TpHit'] == False:
                tradingsymbol = row['TradingSymbol']
                sl_val=0.0
                tp_val=0.0
                trading_price=0.0
                traded_price =  row['Ltp']
                
                is_ce = row['TradingSymbol'][-2:]
                trading_price = getlasttradedprice(row['Strike'],row['Expiry'].date().strftime("%Y-%m-%d"),is_ce)
                trading_price= float(trading_price)
                
                if row['OrderType'] == 'SELL':
                    sl_val = (traded_price + traded_price*.04)
                    tp_val = (traded_price - traded_price*.1)
                else:
                    sl_val = (traded_price - traded_price*.04)
                    tp_val = (traded_price + traded_price*.1)

                if row['OrderType'] == 'SELL':
                    if trading_price <= tp_val or trading_price >= sl_val:
                        #for kite order placement uncomment below

                        '''                 order = kite.place_order(variety=kite.VARIETY_REGULAR,
                                                exchange=kite.EXCHANGE_NSE,
                                                tradingsymbol=row['TradingSymbol'],
                                                transaction_type=kite.TRANSACTION_TYPE_BUY,
                                                quantity=row['Qty'],
                                                product=kite.PRODUCT_MIS,
                                                order_type=kite.ORDER_TYPE_MARKET,
                                                price=trading_price,
                                                validity=None,
                                                disclosed_quantity=None,
                                                trigger_price=None,
                                                squareoff=None,
                                                stoploss=None,
                                                trailing_stoploss=None,
                                                tag="ChartInkScraper") '''
                        
                        #for Alice Blue order placement
                        #ins = alice.get_instrument_by_symbol(symbol= row['TradingSymbol'],exchange='NFO')

                        #ce_order_sl = place_order_aliceblue(ins,25,'BUY')
                        #print(ce_order_sl)
                        #logging.info(ce_order_sl)
                        #print(f"Stop Loss Order for {row['TradingSymbol']} - CE buy placed at -{trading_price}")
                        #logging.info(f" Stop Loss Order for {row['TradingSymbol']} - CE buy placed at -{trading_price}")

                        coll.update_one({"_id":row['_id']},{"$set":{"FinalPrice":trading_price}})
                        coll.update_one({"_id":row['_id']},{"$set":{"FinalTradedDate":datetime.datetime.now()}})
                        if trading_price <= tp_val:
                            coll.update_one({"_id":row['_id']},{"$set":{"TpHit":True}})
                            mtmlossprofit = mtmlossprofit+(traded_price*row['Qty']-trading_price*row['Qty'])
                        else:
                            coll.update_one({"_id":row['_id']},{"$set":{"SlHit":True}})
                            mtmlossprofit = mtmlossprofit+(trading_price*row['Qty']-traded_price*row['Qty'])

                else:
                    #commented below for now since we are dealing with short straddle banknifty right now
                    ''' if trading_price >= tp_val or trading_price <= sl_val:
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
                                            price=trading_price,
                                            validity=None,
                                            disclosed_quantity=None,
                                            trigger_price=None,
                                            squareoff=None,
                                            stoploss=None,
                                            trailing_stoploss=None,
                                            tag="ChartInkScraper")
                        coll.update_one({"_id":row['_id']},{"$set":{"FinalPrice":trading_price}})
                        coll.update_one({"_id":row['_id']},{"$set":{"FinalTradedDate":datetime.datetime.now()}})
                        if trading_price <= sl_val:
                            coll.update_one({"_id":row['_id']},{"$set":{"SlHit": True}})
                            mtmlossprofit = mtmlossprofit+(traded_price*row['Qty']- trading_price*row['Qty'])
                        else:
                            coll.update_one({"_id":row['_id']},{"$set":{"TpHit": True}})
                            mtmlossprofit = mtmlossprofit+ (trading_price*row['Qty']-traded_price*row['Qty']) '''
                    coll.update_one({"_id":row['_id']},{"$set":{"FinalPrice":trading_price}})
                            
            print("ID-"+str(row['_id']) +"  " +"Trading Symbol - "+ row['TradingSymbol'])

    print("The      MTM   amount =="+str(mtmlossprofit))

    #print("Stop loss and Profit Taking loop")
    
if __name__ == '__main__':
    try:
        logging.info('Alice_Blue_API.py...execution started now.....')
        logging.info("Short Straddle Number -1")
        logging.info("**********************************************************")
        schedule.every().day.at("09:20").do(createshortstraddlebnf)
        logging.info("**********************************************************")
        logging.info("Short Straddle Number -2")
        logging.info("**********************************************************")
        schedule.every().day.at("09:50").do(createshortstraddlebnf)
        logging.info("**********************************************************")
        logging.info("Short Straddle Number -3")
        logging.info("**********************************************************")
        schedule.every().day.at("10:15").do(createshortstraddlebnf)
        logging.info("**********************************************************")
        logging.info("Short Straddle Number -4")
        logging.info("**********************************************************")
        schedule.every().day.at("10:45").do(createshortstraddlebnf)
        logging.info("**********************************************************")
        schedule.every(2).minutes.do(check_sl_pt)
        schedule.every(1).minutes.do(calculate_mtm)

        while True:        
        # Checks whether a scheduled task
        # is pending to run or not
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info('Logged out of the program using keyboard interrupt....')

        #code for the most loved screeners
''' df_most_loved_screeners['OccurInDiffScreeners'] = df_bullish.groupby(by="nsecode")['nsecode'].transform('count')
df_most_loved_screeners = df_most_loved_screeners.query(f'OccurInDiffScreeners >{optionMaxOccurence}')
df_most_loved_screeners.drop(['Unnamed: 0','sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
grp_most_loved_screeners =  df_most_loved_screeners.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
grp_most_loved_screeners = grp_most_loved_screeners[grp_most_loved_screeners['OccurInDiffScreeners'] >optionMaxOccurence].sort_values(['OccurInDiffScreeners'],ascending=False) '''