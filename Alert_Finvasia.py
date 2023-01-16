# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 10:13:23 2022

Here i coded how to get live range break alert to telegram group / person using finvasia broker in python.

It is very much beneficial for office going trader like me who can't track share price on screen.

Contact details :
Telegram Channel:  https://t.me/pythontrader
Developer Telegram ID : https://t.me/pythontrader_admin
Youtube Channel : https://www.youtube.com/channel/UCOmQlnekRftjcinwbB_t5HQ
Gmail ID:   mnkumar2020@gmail.com 
Whatsapp : 9470669031 

Disclaimer: The information provided by the Python Traders channel is for educational purposes only, so please contact your financial adviser before placing your trade. Developer is not responsible for any profit/loss happened due to coding, logical or any type of error.
"""

from NorenRestApiPy.NorenApi import  NorenApi
import json
import pandas as pd
from time import sleep
import requests

from datetime import datetime as dt

#you can set this variable as per your requirment, its 30 minute in gap of 30 second it will check and send the alert
Alert_Check_Duration = 30

#please update below telegram credenatil
TelegramBotCredential = '5601294531:AAHG1Y6c9gqB-KALjOWKHP_wV-eYKVrzmpo'
ReceiverTelegramID = '5242432731'

#shoonya/finvasia credential
userid    = 'FA51087'
password =  'Password'
twoFA    =  '1991'
vendor_code = 'FA51087_U'
api_secret = '8f120c8fa44eedfe25ef501d2a34de7e'
imei = 'abc1234'

api = ''

df_Alert_Input = pd.DataFrame() 

def Broker_Login():
    global api
    try:
        class ShoonyaApiPy(NorenApi):
            def __init__(self):
                NorenApi.__init__(self, host='https://shoonyatrade.finvasia.com/NorenWClientTP/', websocket='wss://shoonyatrade.finvasia.com/NorenWSTP/', eodhost='https://shoonya.finvasia.com/chartApi/getdata/')

        api = ShoonyaApiPy()

        login_status = api.login(userid=userid, password=password, twoFA=twoFA, vendor_code=vendor_code, api_secret=api_secret, imei=imei)
        client_name = login_status.get('uname')
        return 1
    
    except Exception as e:
        Message =  str(e) + " : Exception occur in login with broker"
        print(Message)
        return 0
        
def GetToken(exchange,tradingsymbol):
    global api
    Token = api.searchscrip(exchange=exchange, searchtext=tradingsymbol).get('values')[0].get('token')
    return Token

def GetLTP(exchange,Token):
    global api
    ret = api.get_quotes(exchange, str(Token))
    LTP = ret.get('lp')
    return LTP
                                               
def AlertInput_LocalSheet():
    Message = "I am inside AlertInput_LocalSheet"
    print(Message)  
    global df_Alert_Input
    
    #you need to update below variable as per your local sheet name
    df_Alert_Input = pd.read_csv("Alert_input.csv")
    
    df_Alert_Input['Token'] = None
    
    #caculate token for all input
    for ind in df_Alert_Input.index:

        Symbol = df_Alert_Input['Symbol'][ind]
        try:
            Token = GetToken(df_Alert_Input['Exchange'][ind],Symbol)
            df_Alert_Input['Token'][ind] = Token
        except Exception as e:
            print(f"{e} : Error occur while calculating shoonya Token for  {Symbol}")

def AlertInput_GoogleSheet():
    Message = "I am inside AlertInput_GoogleSheet"
    print(Message)  
    global df_Alert_Input
    
    #you need to update below variable as per your sheet detail
    google_sheet_id = "12AbH8L5ORessjE5oTyqOY4SVGjykWxQjyqFu_7EiKwM"
    Google_sheet_name = "Sheet1"

    gsheet_url = "https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet={}".format(google_sheet_id,Google_sheet_name)

    df_Alert_Input = pd.read_csv(gsheet_url)
    
    df_Alert_Input['Token'] = None
    
    #caculate token for all input
    for ind in df_Alert_Input.index:

        Symbol = df_Alert_Input['Symbol'][ind]
        try:
            Token = GetToken(df_Alert_Input['Exchange'][ind],Symbol)
            df_Alert_Input['Token'][ind] = Token
        except Exception as e:
            print(f"{e} : Error occur while calculating shoonya Token for  {Symbol}")
            
def updateLTP():
    Message = "I am inside updateLTP"
    print(Message)
    global df_Alert_Input
    df_Alert_Input['LTP'] = None
    
    for ind in df_Alert_Input.index:
        try:
            if(df_Alert_Input['Alert_ON'][ind] == 1):
                LTP = GetLTP(df_Alert_Input['Exchange'][ind], df_Alert_Input['Token'][ind])
                df_Alert_Input['LTP'][ind] = LTP
        except Exception as e:
            Message =  str(e) + " : Exception occur in Fetching LTP of " + str(df_Alert_Input['Exchange'][ind]) +":" + str(df_Alert_Input['Symbol'][ind]) + " with token =" + str(df_Alert_Input['Token'][ind])
            print(Message)
        
def CheckAlert():
    Message = "I am inside CheckAlert"
    print(Message)
    global df_Alert_Input
    
    for ind in df_Alert_Input.index:
        try:
            if( (df_Alert_Input['Alert_ON'][ind] == 1) & (df_Alert_Input['LTP'][ind] != None) ):
                
                if( (float(df_Alert_Input['If_Below'][ind]) >= float(df_Alert_Input['LTP'][ind]))  ) :
                    Message = "Low Price alert \n\n" + df_Alert_Input['Symbol'][ind] + " current LTP is " + str(df_Alert_Input['LTP'][ind]) + " which is below than your set trigger value " + str(df_Alert_Input['If_Below'][ind]) + " \n\nRemark: " + str(df_Alert_Input['Remark'][ind])
                    
                    print(Message)
                    SendMessageToTelegram(Message)
                    
                    df_Alert_Input['Is_broken'][ind] = 'Low_Broken'
                    
                if( (float(df_Alert_Input['If_Above'][ind]) <= float(df_Alert_Input['LTP'][ind])) & (df_Alert_Input['If_Above'][ind] != None) ) :
                    Message = "High Price Alert \n\n" + df_Alert_Input['Symbol'][ind] + " current LTP is " + str(df_Alert_Input['LTP'][ind]) + " which is higher than your set trigger value " + str(df_Alert_Input['If_Above'][ind]) + " \n\nRemark: " + str(df_Alert_Input['Remark'][ind])
                    
                    print(Message)
                    SendMessageToTelegram(Message)
                    
                    df_Alert_Input['Is_broken'][ind] = 'High_Broken'
                    
        except Exception as e:
            Message =  str(e) + " : Exception occur in CheckAlert"
            print(Message) 

def SendMessageToTelegram(Message):
    try:
        Url = "https://api.telegram.org/bot" + str(TelegramBotCredential) +  "/sendMessage?chat_id=" + str(ReceiverTelegramID)
        
        textdata ={ "text":Message}
        response = requests.request("POST",Url,params=textdata)
    except Exception as e:
        Message = str(e) + ": Exception occur in SendMessageToTelegram"
        print(Message)   
		
def strategy():
    Message = "I am inside strategy"
    print(Message)
    
    global df_Alert_Input
    

    if(Broker_Login() ==1):

        while True:
            try:
                
                #print("\n\n\n\n%%%%%%%%%%%%%%%%AlertInput_LocalSheet%%%%%%%%%%%%%%")
                #AlertInput_LocalSheet()
                #print(df_Alert_Input)

                print("\n\n\n\n%%%%%%%%%%%%%%%%AlertInput_GoogleSheet%%%%%%%%%%%%%%")
                AlertInput_GoogleSheet()
                print(df_Alert_Input)
                
                print("\n\n\n\n%%%%%%%%%%%%%updateLTP%%%%%%%%%%%%%%%%%")
                updateLTP()
                print(df_Alert_Input)
                
                df_Alert_Input['Is_broken'] = None
                
                print("\n\n\n\n%%%%%%%%%%%CheckAlert%%%%%%%%%%%%%%%%%%%")
                CheckAlert()     
                print(df_Alert_Input)
                
                
                sleep(Alert_Check_Duration)
                
                CurrentTime = dt.now().hour * 60 + dt.now().minute
                Alert_Till = 23 * 60 + 50
                if(CurrentTime >= Alert_Till):
                    BBYEMessage = "Bbye, Market has been closed" 
                    SendMessageToTelegram(TelegramSenderId,TelegramUser,BBYEMessage)
                    break
            
            except Exception as e:
                Message = str(e) + ": Exception occur in strategy"
                print(Message)
        
if __name__ == '__main__':  
    strategy()
   