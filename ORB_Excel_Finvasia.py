# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 15:13:23 2022

Here i coded how to automate Open range Break strategy for finvasia broker using python.

Contact details :
Telegram Channel:  https://t.me/pythontrader
Developer Telegram ID : https://t.me/pythontrader_admin
Gmail ID:   mnkumar2020@gmail.com 
Whatsapp : 9470669031 

Disclaimer: The information provided by the Python Traders channel is for educational purposes only, so please contact your financial adviser before placing your trade. Developer is not responsible for any profit/loss happened due to coding, logical or any type of error.
"""

from NorenRestApiPy.NorenApi import  NorenApi
import json
import pandas as pd
import numpy as np
from time import sleep
from datetime import datetime as dt
from datetime import timedelta as td

#credential
userid    = 'FA51087'
password =  'Shoonya123$#'
twoFA    =  '1991'
vendor_code = 'FA51087_U'
api_secret = '8f120c8fa44eedfe25ef501d2a34de7e'
imei = 'abc1234'


sleeptime = 40

df_trade_Input = pd.DataFrame() 
df_order_status = pd.DataFrame()


class ShoonyaApiPy(NorenApi):
        def __init__(self):
            NorenApi.__init__(self, host='https://shoonyatrade.finvasia.com/NorenWClientTP/', websocket='wss://shoonyatrade.finvasia.com/NorenWSTP/', eodhost='https://shoonya.finvasia.com/chartApi/getdata/')

api = ShoonyaApiPy()

login_status = api.login(userid=userid, password=password, twoFA=twoFA, vendor_code=vendor_code, api_secret=api_secret, imei=imei)

def GetToken(exchange,tradingsymbol):
    global api
    Token = api.searchscrip(exchange=exchange, searchtext=tradingsymbol).get('values')[0].get('token')
    return Token

def GetLTP(exchange,Token):
    ret = api.get_quotes(exchange, str(Token))
    LTP = ret.get('lp')
    Message = "LTP =" + str(LTP)
    print(Message)
    return LTP

def order_place(tradingsymbol,exchange,buy_or_sell,quantity,variety='regular',price_type='MKT',product_type='M',price = 0):
    
    Message = "Going to place shoonya order for tradingsymbol = " + str(tradingsymbol)  + ", order_type = " + buy_or_sell + ", quantity = "  + str(quantity) + ", price_type = " + price_type + ", price = " + str(price) + ", product_type = " + str(product_type) 
    
    print(Message)
    global api
    OrderId = api.place_order(buy_or_sell = buy_or_sell, 
                            product_type = product_type,
                            exchange = exchange,
                            tradingsymbol = tradingsymbol, 
                            quantity = quantity,
                            discloseqty=0,
                            price_type = price_type,
                            price = price,
                            trigger_price=None,
                            retention='DAY', 
                            remarks='my_order_001').get('norenordno')  
    Message = "Placed order id :" + OrderId
    print(Message)
	
    return OrderId

def Assign_Token():

    global df_trade_Input
    for ind in df_trade_Input.index:
        if((df_trade_Input['Status'][ind] == 'START')):

            tradingsymbol = df_trade_Input['Symbol'][ind]
            try:
                Token = GetToken(df_trade_Input['Exchange'][ind],tradingsymbol)
                df_trade_Input['Token'][ind] = Token
            except Exception as e:
                print(f"{e} : Error occur while calculating shoonya Token for  {tradingsymbol}")
                df_trade_Input['Status'][ind] = 'WAIT'

def order_status (orderid):
    global api
    filled_quantity = 0
    AverageExecutedPrice = 0
    try:
        order_book = api.get_order_book()
        order_book = pd.DataFrame(order_book)
        
        order_book = order_book[order_book.norenordno == str(orderid)]
        print(order_book)
        
        status = order_book.iloc[0]['status']
        if(status == 'COMPLETE'):
            filled_quantity = 1
            AverageExecutedPrice = order_book.iloc[0]['avgprc']
    except Exception as e:
        Message = str(e) + " : Exception occur in order_status"
        print(Message)
    return filled_quantity, AverageExecutedPrice
    
def GetExecutedPrice (orderid):
    Message = "I am inside GetExecutedPrice for " + str(orderid)
    print(Message)
    global api
    ExecutedPrice = 0
    try:
        order_book = api.get_order_book()
        order_book = pd.DataFrame(order_book)
        
        order_book = order_book[(order_book.norenordno == str(orderid)) & (order_book.status == 'COMPLETE') ]
        #print(order_book)
        
        if(len(order_book) == 1):
            ExecutedPrice = order_book.iloc[0]['avgprc']
        else:
            print("Order not found or not completed")
    except Exception as e:
        Message = str(e) + ": Exception occur in GetExecutedPrice for orderid" + str(orderid)
        print(Message)
    return ExecutedPrice
           
def updateLTP():
    Message = "I am inside updateLTP()"
    print(Message)
    global df_trade_Input
    
    for ind in df_trade_Input.index:
        try:
            if(df_trade_Input['ORB_RANGE'][ind] == 'CALCULATED'):
                exchange = df_trade_Input['Exchange'][ind]
                Token = df_trade_Input['Token'][ind]
                LTP = GetLTP(exchange,Token)
                if(LTP != 0):
                    df_trade_Input['LTP'][ind] = LTP
        except Exception as e:
            Message = str(e) + ": Exception occur in updateLTP for " + df_trade_Input['Symbol'][ind]
            print(Message)   
           
def CheckNewEntry():
    
    Message ="I am inside CheckNewEntry"
    print(Message)
    
    global df_trade_Input
    global df_order_status
    
    updateLTP()
    print(df_trade_Input)
    print(df_order_status)
    for ind in df_trade_Input.index:
        
        try:
        
            Message = "*********************Check " + df_trade_Input['Symbol'][ind]+ " having value ORB_RANGE= " + str(df_trade_Input['ORB_RANGE'][ind]) + "  Trade_Status = " + str(df_trade_Input['Trade_Status'][ind]) + " LTP = " + str(df_trade_Input['LTP'][ind]) + " Trade_setup= "+ str(df_trade_Input['Trade_setup'][ind]) + " URange= " + str(df_trade_Input['URange'][ind]) + " L_BREAK= " + str(df_trade_Input['LRange'][ind])
            print(Message)
                   
            if((df_trade_Input['ORB_RANGE'][ind] == 'CALCULATED') & (df_trade_Input['Trade_Status'][ind] == None) & (df_trade_Input['LTP'][ind] != 0)):
                Message = "*********************Analysing value*********"
                print(Message)
                
                if( ( (df_trade_Input['Trade_setup'][ind] == 'H_BREAK')&(df_trade_Input['URange'][ind] < df_trade_Input['LTP'][ind]) ) or ( (df_trade_Input['Trade_setup'][ind] == 'L_BREAK')&(df_trade_Input['LRange'][ind] > df_trade_Input['LTP'][ind]) ) ):

                    Message =  "Range broke, execute the trade"
                    print(Message)
                    
                    orderid = order_place( df_trade_Input['Symbol'][ind] ,df_trade_Input['Exchange'][ind],'BUY' if df_trade_Input['Trade_setup'][ind] == 'H_BREAK' else 'SELL',int(df_trade_Input['quantity'][ind]),'regular', 'MKT','I')
                            
                    df_trade_Input['Trade_Status'][ind] = 'ENTRY_PLACED'
                    df_trade_Input['EntryOrderId'][ind] = orderid                    
                            
            else:
                Message = "Condition dones't meet to start a trade"
                print(Message)
        
        except Exception as e:
            Message =  str(e) + " : Exception occur in CheckNewEntry for " + df_trade_Input['Symbol'][ind]
            print(Message) 

def updateOrderStatus():
    Message ="I am inside updateOrderStatus"
    print(Message)
    global df_trade_Input
    global AlgoID
    print(df_trade_Input)
    try:
        for ind in df_trade_Input.index:
        
            if(df_trade_Input['Trade_Status'][ind] == 'ENTRY_PLACED' or df_trade_Input['Trade_Status'][ind] == 'EXIT_PLACED'):
               
                Message = "Kindly check Order execution status and update executed price of Symbol= " + str(df_trade_Input['Symbol'][ind])
                
                print(Message)
                
                if(df_trade_Input['Trade_Status'][ind] == 'ENTRY_PLACED'):
                    OrderId = df_trade_Input['EntryOrderId'][ind]
                    
                    Order_Execution_Completed, AverageExecutedPrice = order_status(OrderId)

                    if(Order_Execution_Completed == 1):
                        Message = "Entry successfully executed, so going to update Trade status"
                        print(Message)
                        
                        
                        Target = 0
                        SL = 0
                        if(df_trade_Input['Trade_setup'][ind] == 'H_BREAK'):
                            Target = float(AverageExecutedPrice) + float(df_trade_Input['Target_point'][ind])
                            SL = float(AverageExecutedPrice) - float(df_trade_Input['SL_point'][ind])
                        else:
                            Target = float(AverageExecutedPrice) - float(df_trade_Input['Target_point'][ind])
                            SL = float(AverageExecutedPrice) + float(df_trade_Input['SL_point'][ind])
                            
                        df_trade_Input['Target'][ind] = Target
                        
                        df_trade_Input['SL'][ind] = SL
                        
                        df_trade_Input['EntryPrice'] = AverageExecutedPrice
                    
                        df_trade_Input['Trade_Status'][ind] = 'OPEN'
   
                        
                elif(df_trade_Input['Trade_Status'][ind] == 'EXIT_PLACED'):
                    
                    OrderId = df_trade_Input['ExitOrderId'][ind]
                    
                    Order_Execution_Completed, AverageExecutedPrice = order_status(OrderId)
                
                    if(Order_Execution_Completed == 1):
                        Message = "Exit successfully executed, so going to update order status to EXIT_EXECUTED"
                        
                        
                        Profit = 0
                        if(df_trade_Input['Trade_setup'][ind] == 'H_BREAK'):
                            Profit = (float(AverageExecutedPrice) - float(df_trade_Input['EntryPrice'][ind])) * int(df_trade_Input['quantity'][ind])
                        else:
                            Profit = (float(df_trade_Input['EntryPrice'][ind]) - float(AverageExecutedPrice) ) * int(df_trade_Input['quantity'][ind])
                            
                        df_trade_Input['Profit'][ind] = Profit
                        
                        df_trade_Input['ExitPrice'][ind] = AverageExecutedPrice
                        
                        
                        df_trade_Input['Trade_Status'][ind] = 'CLOSED'
                
    except Exception as e:
        Message =  str(e) + " : Exception occur in updateOrderStatus"
        print(Message) 
                
def CheckExit():
    Message ="I am inside CheckExit"
    print(Message)
    global df_trade_Input
    updateLTP()
    print(df_trade_Input)
    
    for ind in df_trade_Input.index:
        try:
            if(df_trade_Input['Trade_Status'][ind] == 'OPEN'):
                Message = "******************Check Symbol=" + df_trade_Input['Symbol'][ind] +" Symbol=" + str(df_trade_Input['Symbol'][ind])+ " for any trade exit possibilites*****"
                print(Message)
                
                
                Target = float(df_trade_Input['Target'][ind])
                SL = float(df_trade_Input['SL'][ind])
                LTP = float(df_trade_Input['LTP'][ind])
                Message = "Target=" + str(Target) + " SL=" + str(SL) + " LTP=" + str(LTP)
                print(Message)
                if(  ( df_trade_Input['Trade_setup'][ind] == 'H_BREAK' and ((LTP <= SL) or (LTP >= Target ))) or  ( df_trade_Input['Trade_setup'][ind] == 'L_BREAK' and ((LTP >= SL) or (LTP <= Target )))
                ):
                    Message ="SL or Target Hit"
                    print(Message)
                    
                    orderid = order_place( df_trade_Input['Symbol'][ind] ,df_trade_Input['Exchange'][ind],'SELL' if df_trade_Input['Trade_setup'][ind] == 'H_BREAK' else 'BUY',int(df_trade_Input['quantity'][ind]),'regular', 'MKT','I')
            
                    df_trade_Input['ExitOrderId'][ind] = orderid
                        
                    df_trade_Input['Trade_Status'][ind]= 'EXIT_PLACED'
                    
        except Exception as e:
            Message =  str(e) + " : Exception occur in CheckExit for " + df_trade_Input['Symbol'][ind]
            print(Message)    
                       
def HistorialData(exchange, Token, starttime, endtime, interval):
    Message = "I am inside HistorialData"
    print(Message)
    Message =  "Fetching HistorialData for " + str(exchange) + " " + str(Token) + " " + str(starttime) + " " + str(endtime) + " " + str(interval)
    print(Message) 
    global api
    try:
        data = api.get_time_price_series(exchange, Token, starttime, endtime, interval)
        #print(data)
        
        data_df = pd.DataFrame(data)
        print(data_df)
    
    except Exception as e:
        Message =  str(e) + " : Exception occur in HistorialData for " + str(exchange) + " " + str(Token) + " " + str(starttime) + " " + str(endtime) + " " + str(interval)
        print(Message) 
    return data_df
    
def CheckORBInitialise():
    Message = "I am inside CheckORBInitialise"
    print(Message)
    global df_trade_Input
    for ind in df_trade_Input.index:
        try:
            if(df_trade_Input['Status'][ind] == 'START'):
                if(df_trade_Input['ORB_RANGE'][ind] == 'NOT_CALCULATED'):
                    
                    start_hour = df_trade_Input['Candle_Start_Time_H'][ind]
                    start_minute = df_trade_Input['Candle_Start_Time_M'][ind]
                    end_hour = df_trade_Input['Candle_End_Time_H'][ind]
                    end_minute = df_trade_Input['Candle_End_Time_M'][ind]
                    
                    if((end_hour * 60 + end_minute) < (dt.now().hour * 60 + dt.now().minute)):
                    
                        exchange= df_trade_Input['Exchange'][ind]
                        Token= df_trade_Input['Token'][ind]
                        lastBusDay = dt.today() 
                        starttime= lastBusDay.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                        endtime= lastBusDay.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
                        interval = 1

                        data = HistorialData(exchange= exchange,Token= Token,starttime=starttime.timestamp(),endtime=endtime.timestamp(),interval=interval )
                        
                        if(len(data) > 0 ):
                            
                            df_trade_Input['URange'][ind] = data['inth'].max()
                            df_trade_Input['LRange'][ind] = data['intl'].min()
                            
                            df_trade_Input['ORB_RANGE'][ind] = 'CALCULATED'
                            Message =  df_trade_Input['Symbol'][ind]  +  " ORB Calculated"
                            print(Message)
                        else:
                            Message =  df_trade_Input['Symbol'][ind]  +  " Historical data not received"
                            print(Message)
                        
                    else:
                        Message =  df_trade_Input['Symbol'][ind]  +  " ORB end time condition doesn't meet yet"
                        print(Message)
                elif(df_trade_Input['ORB_RANGE'][ind] == 'CALCULATED'):
                    Message =  df_trade_Input['Symbol'][ind]  +  " ORB already calculated"
                    print(Message)
                
        except Exception as e:
            Message =  str(e) + " : Exception occur in CheckORBInitialise for " + df_trade_Input['Symbol'][ind]
            print(Message) 
                       
def Strategy():
    Message = "I am inside Strategy"
    print(Message)
    global df_trade_Input
    
    df_trade_Input = pd.read_csv("Trade_Input.csv")
    
    df_trade_Input['Token'] = None
    df_trade_Input['ORB_RANGE'] = "NOT_CALCULATED"
    df_trade_Input['Trade_Status'] = None
    df_trade_Input['EntryPrice'] = None
    df_trade_Input['EntryOrderId'] = None
    df_trade_Input['ExitPrice'] = None
    df_trade_Input['ExitOrderId'] = None
    df_trade_Input['Target'] = None
    df_trade_Input['SL'] = None
    df_trade_Input['Profit'] = None
    df_trade_Input['URange'] = None
    df_trade_Input['LRange'] = None
    df_trade_Input['LTP'] = None 
    
    Assign_Token()
    
    try:
        while True:
            Message = "\n\n\n\n\n%%%%%%%%%%%%%%CheckORBInitialise%%%%%%%%%%%%%%%%"
            print(Message)
            CheckORBInitialise()
            print(df_trade_Input)
            
            Message = "\n\n\n\n\n%%%%%%%%%%%%%%CheckNewEntry%%%%%%%%%%%%%%%%"
            print(Message)
            CheckNewEntry()
            
            Message = "\n\n\n\n\n%%%%%%%%%%%updateOrderStatus%%%%%%%%%%%%%%%%%%%"
            print(Message)
            updateOrderStatus()  
            
            Message = "\n\n\n\n\n%%%%%%%%%%%%%%%%CheckExit%%%%%%%%%%%%%%"
            print(Message)
            CheckExit()

            CurrentTime = dt.now().hour * 60 + dt.now().minute
            TradeTill = 23 * 60 + 55
            if(CurrentTime >= TradeTill):
                BBYEMessage = "Trade Time over, ORB strategy stopped"
                print(BBYEMessage)
                break
                    
            sleep(sleeptime)    
            
    except Exception as e:
        Message = str(e) +  ": Exception occur in strategy"
        print(Message)
  
if __name__ == '__main__':  
    Strategy()
       