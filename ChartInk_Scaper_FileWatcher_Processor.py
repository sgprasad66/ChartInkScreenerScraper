import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
    
def removefirstcolumn(dataframeinput):
    first_column = dataframeinput.columns[0]
    # Delete first
    dataframeinput = dataframeinput.drop([first_column], axis=1)
    return dataframeinput


def processnewfiles():
    import glob
    import numpy as np
    import os
    import pandas as pd
    from datetime import datetime

    from ChartInk_Scrape_With_Multiprocess import screenmapper
    dfs=[]

    df_1=pd.DataFrame(columns=['','sr','nsecode','name','bsecode','per_chg','close','volume','ScreenerName','TimeOfDay'])
    df_2=pd.DataFrame(columns=['','sr','nsecode','name','bsecode','per_chg','close','volume','ScreenerName','TimeOfDay'])

    from ChartInk_Scrape_With_Multiprocess import screenmapper
    todayfolder = datetime.now().strftime("%d_%m_%Y")
    #all_files = glob.glob("D:\\Python_Trader_Code\\24_12_2022\\*.csv")
    all_files = glob.glob("D:\\Python_Trader_Code\\"+todayfolder+"\*.csv")
    #all_files = glob.glob("D:\\Python_Trader_Code\\datetime.now().strftime(""%d_%m_%Y"")\\*.csv")

    for i,filename in enumerate(all_files, start=0):
        if screenmapper.get('1') in filename:
            df = pd.read_csv(filename)
            df = removefirstcolumn(df)
            df_1 = pd.concat([df_1,df])
            #df_1.to_csv("Bullish.csv")
        elif screenmapper.get('2') in filename:
            df = pd.read_csv(filename)
            df = removefirstcolumn(df)
            df_2 = pd.concat([df_2,df])
            #df_2.to_csv("Bearish.csv")


    df_1.to_csv("Bullish"+"_"+todayfolder+".csv")
    df_2.to_csv("Bearish"+"_"+todayfolder+".csv")

    ''' df_1['OccurInDiffScreeners'] = df_1.groupby(by="nsecode")['nsecode'].transform('count')
    df_1.drop(['sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
    #n=100
    #print(df_1['nsecode'].value_counts()[:n].index.tolist())
    #print((df_1.query('OccurInDiffScreeners >= 15').sort_values(by='OccurInDiffScreeners',ascending= False).groupby(by=['nsecode','ScreenerName','TimeOfDay']).size()))
    df_1 = df_1.query('OccurInDiffScreeners >= 15').sort_values(by='OccurInDiffScreeners',ascending= False).groupby(by=['nsecode','ScreenerName','TimeOfDay']).size()

    df_2['OccurInDiffScreeners'] = df_2.groupby('nsecode')['nsecode'].transform('count')
    df_2.drop(['sr','per_chg','close','name','bsecode','volume'],axis=1,inplace=True)
    #print(df_2.nlargest(200,columns='OccurInDiffScreeners'))
    #print((df_2.query('OccurInDiffScreeners >= 15').sort_values(by='OccurInDiffScreeners',ascending= False).groupby(by=['nsecode','ScreenerName','TimeOfDay']).size()))
    df_2 = df_2.query('OccurInDiffScreeners >= 15').sort_values(by='OccurInDiffScreeners',ascending= False).groupby(by=['nsecode','ScreenerName','TimeOfDay']).size() '''
    df_1['OccurInDiffScreeners'] = df_1.groupby(by="nsecode")['nsecode'].transform('count')
    i=10
    df_1 = df_1.query(f'OccurInDiffScreeners >{i}')
    print(df_1)

    df_2['OccurInDiffScreeners'] = df_2.groupby(by="nsecode")['nsecode'].transform('count')
    i=10
    df_2 = df_2.query(f'OccurInDiffScreeners >{i}')
    print(df_2)

    return df_1,df_2




class Watcher:
    DIRECTORY_TO_WATCH = "D:/Python_Trader_Code/"+datetime.now().strftime("%d_%m_%Y")+"/"
    
    #DIRECTORY_TO_WATCH = "D:/Python_Trader_Code/24_12_2022/"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
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

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print ("Received modified event - %s." % event.src_path)


if __name__ == '__main__':
    w = Watcher()
    w.run()

