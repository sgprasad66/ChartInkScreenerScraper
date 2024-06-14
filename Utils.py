from enum import Enum
import json
import helper
import portalocker
import pymongo
import logging
import configparser
import PySimpleGUI as sg
import subprocess
from datetime import datetime
import pandas as pd
from dataclasses import dataclass
from win10toast import ToastNotifier
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime,MetaData,Select,text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy as db
from sqlalchemy import update
from abc import ABC, abstractmethod


config = helper.read_config()
positions_today_filename_path = config["DaysPositionsSettings"]["PositionsFilePath"]
repository_setting=config["RepositorySettings"]["RepositoryMode"]
mongodbclient = config["MongoDBSettings"]["mongodbclient"]
databasename = config["MongoDBSettings"]["databasename"]
collectionname = config["MongoDBSettings"]["collectionname"]
log_filename_path = config["Logger"]["LogFilePath"]
log_file_Name = config["Logger"]["LogFileName"]
traded_date=datetime.now().strftime("%d_%m_%Y")
sl_index_options = config["SLandTPSettings"]["sl_index_options"]
tp_index_options = config["SLandTPSettings"]["tp_index_options"]
sl_stock_options = config["SLandTPSettings"]["sl_stock_options"]
tp_stock_options = config["SLandTPSettings"]["tp_stock_options"]

sl_options_hedged = config["SLandTPSettingsForHegdedPositions"]["sl_index_options"]
tp_options_hedged = config["SLandTPSettingsForHegdedPositions"]["tp_index_options"]



backdays=5
optionMaxOccurence=5
optionMaxOccurence=5
df_bull=pd.DataFrame()
df_bear=pd.DataFrame()
df_intrabull=pd.DataFrame()
df_intrabear=pd.DataFrame()

logging.basicConfig(
        filename=log_filename_path + "//" + log_file_Name,
        #format="%(asctime)s %(message)s",
        format = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level=20,
    )
class MultiLegStrategy(Enum):
    ''' 2_Calls_Buy_ATM_and_1_Call_Sell_Deep_ITM = 1
    2_Put_Buy_ATM_and_1_Put_Sell_Deep_ITM = 2
    1_Put_ATM_Sell_1_Call_ATM_Sell = 3
    1_Nifty_Call_Buy_1_BankNifty_Put_Buy = 4
    1_Nifty_Put_Buy_1_BankNifty_Call_Buy = 5
    1_Nifty_Call_Buy = 6
    1_Nifty_Put_Buy = 7
    1_BankNifty_Call_Buy = 8
    1_BankNifty_Put_Buy = 9 '''

@dataclass
class trade_real_time_data():
	"""A class for holding REAL-TIME DATA related to the trades"""

	# Attributes Declaration
	# using Type Hints

	order_id: str
	strategy_id: str
	is_hedged: bool
	is_squaredoff:bool
	original_traded_price:float
	realtime_price:float
	squaredoff_price:float
	sl_price: float
	tp_price:float
	sl_hit:bool
	tp_hit:bool
	order_type:str


class stockitem:
    def __init__(
        self,
        instrument_token,
        order_id,
        last_price,
        quantity,
        ordertype,
        tphit,
        slhit,
        finalprice,
        producttype,
        strike=None,
        expiry=None,
        strategy_id=None,
        is_hedged=False
    ):
        self.instrument_token = instrument_token
        self.order_id = order_id
        self.last_price = last_price
        self.quantity = quantity
        self.ordertype = ordertype
        self.tp_hit = False
        self.sl_hit = False
        self.final_price = 0.0
        self.final_value = 0.0
        self.producttype = producttype
        self.strike = strike
        self.expiry = expiry
        self.traded_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #datetime.today()
        self.final_traded_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #datetime.today()
        self.strategy_id=strategy_id
        self.is_hedged=is_hedged

    def getfinalvalue(self):
        self.final_value = self.quantity * self.final_price
        return self.final_value
    
    def setstrategyid(self,ishedged):
        self.is_hedged = ishedged
    
    def setwhetherhedgedornot(self,id):
        self.strategy_id = id
    
    def create_real_time_data_object(self,rt_data: trade_real_time_data):
        rt_data.order_id = self.order_id
        rt_data.strategy_id = self.strategy_id
        rt_data.is_hedged=self.is_hedged
        rt_data.original_traded_price=self.last_price
        rt_data.realtime_price=self.last_price
        rt_data.sl_hit=self.sl_hit
        rt_data.tp_hit=self.tp_hit
        rt_data.squaredoff_price=self.final_price
        rt_data.sl_price=0.0
        rt_data.tp_price=0.0
        rt_data.order_type=self.ordertype
        rt_data.is_squaredoff=False

        return rt_data

    
def stock_alert_notifier(message):
    toast = ToastNotifier()
    toast.show_toast(message)

def read_ini_file(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

def decide_persistence_mechanism():
        
        if repository_setting == "1":
            return JsonFileRepository()
        elif repository_setting == "2":
            return MongoDBRepository()
        else:
            return MySQLRepository() 
        
def create_gui(config):
    layout = []
    for section in config.sections():
        layout.append([sg.Text(f"[{section}]")])
        for key in config[section]:
            layout.append([sg.Text(key), sg.InputText(default_text=config[section][key], key=key)])

    layout.append([sg.Button("Save",key='-Save-')])
    #layout.append([autoscroll=True])
    return [sg.Column(layout,scrollable=True)]

def write_ini_file(file_path,config,values):
    for section in config.sections():
        for key in config[section]:
            config.set(f"{section}",f"{key}",values[f"{key}"])
    #config_file = configparser.ConfigParser()
    with open(file_path, 'w') as configfileObj:
        config.write(configfileObj)
        configfileObj.flush()
        configfileObj.close()
    ''' for section in config.sections():
        config.set()
    write(file_path) '''

def start_service(service_name):
  subprocess.call(["sc", "start", service_name])

def stop_service(service_name):
  subprocess.call(["sc", "stop", service_name])

def convertdataframe(df):
    #if df is not None :
    if df.empty == False:
        df['OccurInDiffScreeners'] = df.groupby(by="nsecode")['nsecode'].transform('count')
        df = df.query(f'OccurInDiffScreeners >{optionMaxOccurence}')
        df.drop(['sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
        grp_bullish =  df.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
        grp_bullish = grp_bullish[grp_bullish['OccurInDiffScreeners'] >optionMaxOccurence].sort_values(['OccurInDiffScreeners'],ascending=False)
        return   grp_bullish

def process(days):
    import glob
    import numpy as np
    import os
    import pandas as pd
    import datetime
    global file_dict
    dates=[]
    file_dict={}

    df1=pd.DataFrame()
    df2=pd.DataFrame()
    df3=pd.DataFrame()
    df4=pd.DataFrame()

    path = "D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\"
    #path="Z:\ChartInk_Scraped_Files\\"
    todayfolder = datetime.datetime.today().strftime("%d_%m_%Y")
    if days <= 1:
        dates.append(todayfolder)
    else:
        for index in range(0,days):
            prev_day = datetime.datetime.today() - datetime.timedelta(days=index)
            dates.append(prev_day.strftime("%d_%m_%Y"))

    print(dates)
    for date in dates:
        if os.path.exists(path+date):
            processnewfiles(date)

            if 'bullish-screeners' in file_dict.keys():
                df1=file_dict['bullish-screeners']
            if 'bearish-screeners' in file_dict.keys():
                df2=file_dict['bearish-screeners']
            if 'intraday-bullish-screeners' in file_dict.keys():
                df3=file_dict['intraday-bullish-screeners']
            if 'intraday-bearish-screeners' in file_dict.keys():
                df4=file_dict['intraday-bearish-screeners']

    return df1,df2,df3,df4

def processnewfiles(processdate):
    import glob
    import numpy as np
    import os
    import pandas as pd
    global file_dict

    all_files = glob.glob("D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\"+processdate+"\*.csv")
    #all_files = glob.glob("Z:\ChartInk_Scraped_Files\\"+processdate+"\*.csv")

    
    for i,filename in enumerate(all_files, start=0):
        file1 = filename.split('\\')[-1]
        file = file1.split('_')[3]
        key = file
        df = pd.read_csv(filename)
        df = removefirstcolumn(df)
        if file_dict.get(key) is None:
            file_dict[key]= pd.DataFrame()
        file_dict[key] = pd.concat([file_dict.get(key),df])

def removefirstcolumn(dataframeinput):
    first_column = dataframeinput.columns[0]
    # Delete first
    dataframeinput = dataframeinput.drop([first_column], axis=1)
    return dataframeinput

class json_file_repository:

    #file_name=None

    def __init__(self,filename=''):
        if filename == '':
            self.file_name = positions_today_filename_path + "\\" + datetime.now().strftime("%d_%m_%Y")+".json"
        else:
            self.file_name = positions_today_filename_path + "\\" + filename +".json"
    

    def update_json_file(self,id_value,update_field,update_value):
        import json

        # Read the JSON data from your file (replace 'your_file.json' with the actual file path)
        data = self.read_file_with_lock()

        if len(data) != 0:
            # Specify the unique 'norenordno' value for the record you want to update
            target_norenordno = id_value  # Replace with the actual value

            # Find the record with the specified 'norenordno'
            for item in data:
                if item.get('OrderId', {}) == target_norenordno:
                    # Update the 'FinalPrice' field to zero
                    item[f'{update_field}'] = update_value
                    break  # Stop searching once the record is found

            # Write the modified data back to the file
            self.write_file_with_lock(data)
            
            #print(f"Updated {update_field}  - field for record with norenordno '{target_norenordno}' to {update_value}.")
    

    def read_file_with_lock(self):
        try:
            with open(self.file_name, 'r') as json_file:
                portalocker.lock(json_file, portalocker.LOCK_EX)
                data = json.load(json_file)
                portalocker.unlock(json_file)
        except PermissionError as excep:
            print("Permission denied:", excep)
        except FileNotFoundError:
            data = []
        except OSError as e:
            print("Error opening file:", e)
        return data
    
    def write_file_with_lock(self,data):
        try:
        # Open the file in write mode
            with open(self.file_name, "w") as file:
                # Acquire exclusive lock on the file
                portalocker.lock(file, portalocker.LOCK_EX)

                # Perform operations on the file
                json.dump(data,file,indent=4)

                # Release the lock
                portalocker.unlock(file)
        except PermissionError as excep:
            print("Permission denied:", excep)
        except FileNotFoundError as ex:
            print("File not found:", ex)
        except OSError as e:
            print("Error opening file:", e)
             
    def add_record(self,new_record):
        data = self.read_file_with_lock()
        data.append(new_record)
        self.write_file_with_lock(data)

def get_traded_records(tradeddate, is_cumulative):
    # global listoftrades
    print("Inside get_traded_records of Finvasia_Get_Strike_From_Given_Premium.py.........")
    import pandas as pd
    if repository_setting == "2":
        try:
            listoftrades = pd.DataFrame()
            coll = client[databasename][tradeddate]
            listoftrades = pd.DataFrame(list(coll.find({})))
            return listoftrades
        except Exception as e :
            logging.error(e)
    else:
        file_repo = json_file_repository()
        data = file_repo.read_file_with_lock()
        dict_data = data #eval(data)
        df_dict = pd.DataFrame(dict_data)
    return df_dict

def update_trades(id_value,update_field,update_value): 
    coll = client[databasename][collectionname]
    if repository_setting == "2":
        try:
            coll.update_one({"_id": id_value}, {"$set": {update_field: update_value}})
        except Exception as e:
            logging.error(e)
    else:
        json_file_repo = json_file_repository()
        json_file_repo.update_json_file(id_value,update_field,update_value)

def get_sl_tp_values(strategy_id,traded_price,order_type):
    id = strategy_id.split('_')[0]
    stk_or_idx_option = strategy_id.split('_')[1]

    if stk_or_idx_option == "OPTSTK":
        if order_type == "SELL" or order_type  == "S" :
            sl_val = traded_price + traded_price * float(sl_stock_options) #0.1   #0.35
            tp_val = traded_price - traded_price * float(tp_stock_options) #0.2   # 0.7
        else:
            sl_val = traded_price - traded_price * float(sl_stock_options) #0.1   # 0.35
            tp_val = traded_price + traded_price * float(tp_stock_options) #0.2   # 0.7  
    else:
        if order_type == "SELL" or order_type  == "S" :
            sl_val = traded_price + traded_price * float(sl_index_options) # 0.1   #0.35
            tp_val = traded_price - traded_price * float(tp_index_options) #0.2   # 0.7
        else:
            sl_val = traded_price - traded_price * float(sl_index_options) #0.1   # 0.35
            tp_val = traded_price + traded_price * float(tp_index_options) #0.2   # 0.7  
    return sl_val,tp_val

    ''' def get_sl_tp_values(strategy_id,traded_price,order_type,realtime_price,is_hedged):
    id = strategy_id.split('_')[0]
    stk_or_idx_option = strategy_id.split('_')[1]
    sl_price_hedged=0.0
    tp_price_hedged=0.0

    sl_price_hedged

    calc_price = traded_price
    if realtime_price > traded_price :
        calc_price = realtime_price

    if is_hedged == True :
        sl_price = sl_options_hedged
        tp_price = tp_options_hedged
    elif :
        sl_price = sl_options
        tp_price = tp_options 

    if stk_or_idx_option == "OPTSTK":
        if order_type == "SELL" or order_type  == "S" :
            sl_val = calc_price + calc_price * float(sl_stock_options) #0.1   #0.35
            tp_val = calc_price - calc_price * float(tp_stock_options) #0.2   # 0.7
        else:
            sl_val = calc_price - calc_price * float(sl_stock_options) #0.1   # 0.35
            tp_val = calc_price + calc_price * float(tp_stock_options) #0.2   # 0.7  
    else:
        if order_type == "SELL" or order_type  == "S" :
            sl_val = calc_price + calc_price * float(sl_index_options) # 0.1   #0.35
            tp_val = calc_price - calc_price * float(tp_index_options) #0.2   # 0.7
        else:
            sl_val = calc_price - calc_price * float(sl_index_options) #0.1   # 0.35
            tp_val = calc_price + calc_price * float(tp_index_options) #0.2   # 0.7  
    print(f"Strategy_id - {strategy_id}")
    print(f"Traded Price - {traded_price}")
    print(f"Stop Loss Value - {sl_val}")
    print(f"Take Profit Value - {tp_val}")
    
    return sl_val,tp_val '''

class AbstractRepository(ABC):
    @abstractmethod
    def get_traded_records(self):
        pass

    @abstractmethod
    def get_traded_record(self,id_value):
        pass

    @abstractmethod
    def get_historical_traded_records(self):
        pass

    @abstractmethod
    def insert_trade(self,DailyTrades):
        pass

    @abstractmethod
    def update_trade(self,id_value,update_field,update_value):
        pass

Base = declarative_base()

# Define the DailyTrades class
class DailyTrades(Base):
    __tablename__ = 'DailyTrades'
    OrderId = Column(String(20), primary_key=True)
    TradingSymbol = Column(String(50))
    Qty = Column(Integer)
    Ltp = Column(Float)
    OrderType = Column(String(10))
    TpHit = Column(Boolean)
    SlHit = Column(Boolean)
    FinalPrice = Column(Float)
    ProductType = Column(String(10))
    TradedDate = Column(DateTime)
    FinalTradedDate = Column(DateTime)
    Strike = Column(Integer)
    Expiry = Column(String(10))
    StrategyId = Column(String(20))
    IsHedged = Column(Boolean)


class MySQLRepository(AbstractRepository):
    def __init__(self):  
        self.engine=create_engine('mysql://root:Afterlife56@localhost/ChartInkTradeLog')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_traded_records(self):
        sql = text("SELECT * from dailytrades") 
        with self.engine.connect() as conn:
            result = conn.execute(sql).fetchall()
        return pd.DataFrame(result)
        
    def get_historical_traded_records(self):
        sql = text("SELECT * from historydailytradesnew") 
        with self.engine.connect() as conn:
            result = conn.execute(sql).fetchall()
        return pd.DataFrame(result)

    def get_traded_record(self,id_value):
        pass

    
    def insert_trade(self,daily_trade):
        try:
            obj = self.convert_stockitem_to_dailytrades(daily_trade)
            self.session.add(obj)
            self.session.commit()
        except Exception as e:
            logging.error(e)

    def convert_stockitem_to_dailytrades(self,order):
        dailytrades = DailyTrades()
        dailytrades.OrderId = order["OrderId"]
        dailytrades.TradingSymbol = order["TradingSymbol"]
        dailytrades.Qty = order["Qty"]
        dailytrades.Ltp = order["Ltp"]
        dailytrades.OrderType = order["OrderType"]
        dailytrades.TpHit = order["TpHit"]
        dailytrades.SlHit = order["SlHit"]
        dailytrades.FinalPrice = order["FinalPrice"]
        dailytrades.ProductType = order["ProductType"]
        dailytrades.TradedDate = order["TradedDate"]
        dailytrades.FinalTradedDate = order["FinalTradedDate"]
        dailytrades.Strike = order["Strike"]
        dailytrades.Expiry = order["Expiry"]
        dailytrades.StrategyId = order["StrategyId"]
        dailytrades.IsHedged = order["IsHedged"]
        return dailytrades

    def update_trade(self,id_value,update_field,update_value):
        try:

            id_field_exp = f'DailyTrades.OrderId = \"{id_value}\"'
            trade_to_update = self.session.query(DailyTrades).filter(text(id_field_exp)).first()
            if trade_to_update is not None:
                setattr(trade_to_update, update_field, update_value)
                self.session.commit()
                self.session.close()
            else:
                logging.error("Unable to Update at this time..Try again")
        except Exception as e:
            logging.error(e)


class MongoDBRepository(AbstractRepository):
    
    def __init__(self):  
        self.client = pymongo.MongoClient(mongodbclient, ssl=False)
        self.collection = self.client[databasename][traded_date]

    def get_traded_records(self):
        try:
            listoftrades = pd.DataFrame()
            listoftrades = pd.DataFrame(list(self.collection.find({})))
            return listoftrades
        except Exception as e :
            logging.error(e)
    
    def get_historical_traded_records(self):
        pass

    def get_traded_record(self,id_value):
        pass

    
    def insert_trade(self,daily_trade):
        try:
            x = self.client.insert_many(daily_trade)
        except Exception as e :
            logging.error(e)

    def update_trade(self,id_value,update_field,update_value):
        try:
            self.collection.update_one({"_id": id_value}, {"$set": {update_field: update_value}})
        except Exception as e:
            logging.error(e)


class JsonFileRepository(AbstractRepository):

    def __init__(self,filename=''):
        if filename == '':
            self.file_name = positions_today_filename_path + "\\" + datetime.now().strftime("%d_%m_%Y")+".json"
        else:
            self.file_name = positions_today_filename_path + "\\" + filename +".json"

    def get_traded_records(self):
        try:
            data = self.read_file_with_lock()
            dict_data = data #eval(data)
            df_dict = pd.DataFrame(dict_data)
        except Exception as e:
            logging.error(e)
        return df_dict
    
    def get_historical_traded_records(self):
        pass

    def get_traded_record(self,id_value):
        pass

    
    def insert_trade(self,daily_trade):
        data = self.read_file_with_lock()
        data.append(daily_trade)
        self.write_file_with_lock(data)

    def update_trade(self,id_value,update_field,update_value):
        import json

        # Read the JSON data from your file (replace 'your_file.json' with the actual file path)
        data = self.read_file_with_lock()

        if len(data) != 0:
            # Specify the unique 'norenordno' value for the record you want to update
            target_norenordno = id_value  # Replace with the actual value

            # Find the record with the specified 'norenordno'
            for item in data:
                if item.get('OrderId', {}) == target_norenordno:
                    # Update the 'FinalPrice' field to zero
                    item[f'{update_field}'] = update_value
                    break  # Stop searching once the record is found

            # Write the modified data back to the file
            self.write_file_with_lock(data)
            
            #print(f"Updated {update_field}  - field for record with norenordno '{target_norenordno}' to {update_value}.")

    def read_file_with_lock(self):
        try:
            with open(self.file_name, 'r') as json_file:
                portalocker.lock(json_file, portalocker.LOCK_EX)
                data = json.load(json_file)
                portalocker.unlock(json_file)
        except PermissionError as excep:
            print("Permission denied:", excep)
        except FileNotFoundError:
            data = []
        except OSError as e:
            print("Error opening file:", e)
        return data
    
    def write_file_with_lock(self,data):
        try:
        # Open the file in write mode
            with open(self.file_name, "w") as file:
                # Acquire exclusive lock on the file
                portalocker.lock(file, portalocker.LOCK_EX)

                # Perform operations on the file
                json.dump(data,file,indent=4)

                # Release the lock
                portalocker.unlock(file)
        except PermissionError as excep:
            print("Permission denied:", excep)
        except FileNotFoundError as ex:
            print("File not found:", ex)
        except OSError as e:
            print("Error opening file:", e)
#  Start the service
#start_service("MyService")

# Stop the service
#stop_service("MyService")
