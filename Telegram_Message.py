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

#TelegramBotCredential = '5747611163:AAFqIPOxRGTXP25py8mNdXRL7mz-TfsouO8'
#ReceiverTelegramID = '5242432731' #my personal id

#TelegramBotCredential = '69741111df1efdb5f25f6afd5eb0e098'
TelegramBotCredential = '6106136909:AAEWKu4Xk1QtoIjMnoZzblRdc5SZdcntOTY'
ReceiverTelegramID='5416986599'



def SendMessageToTelegram(Message):
    try:
        Url = "https://api.telegram.org/bot" + str(TelegramBotCredential) +  "/sendMessage?chat_id=" + str(ReceiverTelegramID)+"&text=HIHello"
        
        #textdata ={ "text":Message}
        response = requests.request("POST",Url)
        print(response)
    except Exception as e:
        Message = str(e) + ": Exception occur in SendMessageToTelegram"
        print(Message)  

import telegram

def send_mess(text):
    #token = "XXXXXX"
    #chat_id = "XXXXXX"
    try:
        bot = telegram.Bot(token=TelegramBotCredential)
        bot.sendMessage(chat_id=ReceiverTelegramID, text=text)	
        print("Done")
    except Exception as e:
        Message = str(e) + ": Exception occur in send_mess"
        print(Message)  
import requests

def send_to_telegram(message):

    apiURL = f'https://api.telegram.org/bot{TelegramBotCredential}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': ReceiverTelegramID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)

send_to_telegram("Hello from Python!")
		
def SendTelegramFile(FileName):
    Documentfile={'document':open(FileName,'rb')}
    
    Fileurl = "https://api.telegram.org/bot" + str(TelegramBotCredential) +  "/sendDocument?chat_id=" + str(ReceiverTelegramID)
      
    response = requests.request("POST",Fileurl,files=Documentfile)
	
#send_mess("HiHi")
#SendMessageToTelegram("HI")