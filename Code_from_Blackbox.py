import json
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime,MetaData,Select,text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy as db
from sqlalchemy import update
from abc import ABC, abstractmethod


class AbstractRepository(ABC):
    @abstractmethod
    def get_traded_records(self):
        pass

    @abstractmethod
    def get_traded_record(self,id_value):
        pass

    @abstractmethod
    def insert_trade(self,DailyTrades):
        pass

    @abstractmethod
    def update_trade(self,id_value,update_field,update_value):
        pass

Base = declarative_base()

# Define the DailyTrades class
class HistoryDailyTrades(Base):
    __tablename__ = 'History_DailyTrades'
    Historyid = Column(String(20), primary_key=True)
    OrderId = Column(String(20))
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
        return result
    
    def get_traded_record(self,id_value):
        pass

    
    def insert_trade(self,daily_trade):
        self.session.add(daily_trade)
        self.session.commit()

    def update_trade(self,id_value,update_field,update_value):
        id_field_exp = f'DailyTrades.OrderId = \"{id_value}\"'
        trade_to_update = self.session.query(DailyTrades).filter(text(id_field_exp)).first()
        setattr(trade_to_update, update_field, update_value)
        self.session.commit()
        self.session.close()

class MongoDBRepository(AbstractRepository):
    def __init__(self):  
        self.client = pymongo.MongoClient(mongodbclient, ssl=False)
        self.collection = client[databasename][tradeddate]

    def get_traded_records(self):
        try:
            listoftrades = pd.DataFrame()
            listoftrades = pd.DataFrame(list(self.collection.find({})))
            return listoftrades
        except Exception as e :
            logging.error(e)
    
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


# Driver code
R = MySQLRepository()
R.insert_trade(DailyTrades(OrderId='12345', TradingSymbol='NIFTY', Qty=1))
R.update_trade("24060700341058","FinalPrice",666.0)
res = R.get_traded_records()
for record in res:
    print("\n", record)

# Create a database engine
''' engine = create_engine('mysql://root:Afterlife56@localhost/')

# Create a database
#engine.execute('CREATE DATABASE TradeData')

# Create a database engine for the new database
with engine.connect() as conn:
    result = conn.execute('CREATE DATABASE TradeData') '''

''' engine = create_engine('mysql://root:Afterlife56@localhost/ChartInkTradeLog')

# Create the table
Base.metadata.create_all(engine) '''

''' engine = create_engine('mysql://root:Afterlife56@localhost/ChartInkTradeLog')


# Load the JSON data
with open('07_06_2024.json') as f:
    data = json.load(f)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Insert the data into the table
for item in data:
    daily_trade = DailyTrades(
        OrderId=item['OrderId'],
        TradingSymbol=item['TradingSymbol'],
        Qty=item['Qty'],
        Ltp=item['Ltp'],
        OrderType=item['OrderType'],
        TpHit=item['TpHit'],
        SlHit=item['SlHit'],
        FinalPrice=item['FinalPrice'],
        ProductType=item['ProductType'],
        TradedDate=item['TradedDate'],
        FinalTradedDate=item['FinalTradedDate'],
        Strike=item['Strike'],
        Expiry=item['Expiry'],
        StrategyId=item['StrategyId'],
        IsHedged=item['IsHedged']
    )
    session.add(daily_trade)

# Commit the changes
session.commit()

# Close the session
session.close() '''

#from sqlalchemy as db
engine = create_engine('mysql://root:Afterlife56@localhost/ChartInkTradeLog')


conn = engine.connect() 
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

Session = sessionmaker(bind=engine)
session = Session()
 
# SELECT * FROM PROFILE
result = session.query(DailyTrades).all()
 
# VIEW THE RESULT
print("Count:", result[0])

row = session.query(DailyTrades).filter(DailyTrades.OrderId == "24060700341058").first()
row.FinalPrice = 18.4

''' upd = update(DailyTrades)
upd = upd.values({"FinalPrice":555})
upd = upd.where(DailyTrades.OrderId == "24060700341058") '''

session.commit()
# Close the session
session.close()

''' with engine.connect() as conn:
    conn.execute(upd)

sql = text("SELECT * from dailytrades") 
with engine.connect() as conn:
    result = conn.execute(sql).fetchall()

# View the records
for record in result:
    print("\n", record)


session.commit()
# Close the session
session.close()  '''

''' metadata = db.MetaData() #extracting the metadata
dailytrades= db.Table('dailytrades', metadata, autoload=True) #Table object '''
''' meta = db.MetaData()
#db.MetaData.reflect(meta)
meta.reflect(bind=engine)

DailyTrades_Table = meta.tables['dailytrades']
 
# SQLAlchemy Query to select all rows with 
# fiction genre
#query = db.select(DailyTrades_Table)    #.where(BOOKS.c.genre == 'fiction')
 
# Fetch all the records
result = engine.execute(query).fetchall()
 
# View the records
for record in result:
    print("\n", record) 
tab = engine.table('dailytrades')
with engine.connect() as conn:
    #result = conn.execute(dailytrades.select(10)).fetchall()
    result = conn.execute(db.select([DailyTrades_Table])).fetchall()
# Retrieve the data
#daily_trades = session.query('select * from dailytrades').all()

# Print the data
    for daily_trade in result:
        print(daily_trade.OrderId, daily_trade.TradingSymbol, daily_trade.Qty, daily_trade.Ltp)

# Close the session
#session.close() '''