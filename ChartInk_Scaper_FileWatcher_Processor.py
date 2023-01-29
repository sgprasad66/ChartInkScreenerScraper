import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

from kite_trade import *

maxitemcount=10
    
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
    tradeusingkite(grp_bullish,grp_bearish)


def tradeusingkite(bullish,bearish):
    print(bullish['nsecode'])
    print(bullish['OccurInDiffScreeners'])
    
    import pandas as pd
    #enctoken = "zIHb6tJAjlPNKlWePko2v4RKCp8G9kKll4X5KTeGx16/xMjPb2pieapxQUxdmxZ8NaPiZhv3LQscrvFfpHb5wujmx3H+TNRW430TliWs/NHlwo10Vd+ywQ=="
    enctoken =  "qaQ42nquhvrFpn5YQnBwZPyINT/LMdt0mVDjVJaK7OqDg79kdOjCDmThXjWSs1SzVAg7K5SIfVvanld734sC+l1c2jdNT0h4iFQtjaEXiQPZutQ0etyvGA=="
    kite = KiteApp(enctoken=enctoken)

    #print(kite.margins())
    #print(kite.baskets())

    #ff = print(kite.instruments())
    print(kite.quote(["NSE:NIFTY BANK", "NSE:ACC", "NFO:NIFTY22SEPFUT"]))

    #import datetime
    #instrument_token = 9604354
    #from_datetime = datetime.datetime.now() - datetime.timedelta(days=7)     # From last & days
    #to_datetime = datetime.datetime.now()
    #interval = "5minute"
    #print(kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False))
    symbol = ""
    if bullish.iloc[0].empty == False:
        print(symbol)
        symbol= bullish.iloc[0]['nsecode']

    # Place Order
    order = kite.place_order(variety=kite.VARIETY_AMO,
                            exchange=kite.EXCHANGE_NSE,
                            tradingsymbol=symbol,
                            transaction_type=kite.TRANSACTION_TYPE_BUY,
                            quantity=1,
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

