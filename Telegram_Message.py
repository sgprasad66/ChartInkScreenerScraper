# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 01:13:23 2022

Here i coded how to send a message/file to telegram user/group using python

Contact details :
Telegram Channel:  https://t.me/pythontrader
Developer Telegram ID : https://t.me/pythontrader_admin
Gmail ID:   mnkumar2020@gmail.com 
Whatsapp : 9470669031 

Disclaimer: The information provided by the Python Traders channel is for educational purposes only, so please contact your financial adviser before placing your trade. Developer is not responsible for any profit/loss happened due to coding, logical or any type of error.
"""
#link to get user id/ group id or any activity related to our bot
#https://api.telegram.org/bot5747611163:AAFqIPOxRGTXP25py8mNdXRL7mz-TfsouO8/getUpdates


import requests

#please generate your bot and update TelegramBotCredential and ReceiverTelegramID below :

TelegramBotCredential = '5747611163:AAFqIPOxRGTXP25py8mNdXRL7mz-TfsouO8'
ReceiverTelegramID = '5242432731' #my personal id


def SendMessageToTelegram(Message):
    try:
        Url = "https://api.telegram.org/bot" + str(TelegramBotCredential) +  "/sendMessage?chat_id=" + str(ReceiverTelegramID)
        
        textdata ={ "text":Message}
        response = requests.request("POST",Url,params=textdata)
    except Exception as e:
        Message = str(e) + ": Exception occur in SendMessageToTelegram"
        print(Message)  
		
		
def SendTelegramFile(FileName):
    Documentfile={'document':open(FileName,'rb')}
    
    Fileurl = "https://api.telegram.org/bot" + str(TelegramBotCredential) +  "/sendDocument?chat_id=" + str(ReceiverTelegramID)
      
    response = requests.request("POST",Fileurl,files=Documentfile)
	

SendMessageToTelegram("HI")