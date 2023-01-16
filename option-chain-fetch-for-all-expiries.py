import requests
import pandas as pd
import xlwings as xw
import time
import openpyxl

url = "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY"
url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
headers = {"accept-encoding": "gzip, deflate, br",
            "accept-language":"en-GB,en-US;q=0.9,en;q=0.8",
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}

session = requests.Session()
df=[]
loopcount=0
while True:
    loopcount=loopcount+1
    data = session.get(url,headers=headers).json()["records"]["data"]

    ocdata = []

    for i in data:
        for j,k in i.items():
            if j=='CE' or j=='PE':
                info=k
                info['instrumentType']=j
                ocdata.append(info)

    #df.concat(pd.DataFrame(ocdata))
    df.append(pd.DataFrame(ocdata))
    print(df)

    #filename = r'D:\Python_Trader_Code\All_Expiries.xlsx'

    ##workbook_master=openpyxl.load_workbook(filename)

    #writer=pd.ExcelWriter(filename,engine='openpyxl',mode='a')
    #writer.sheets = dict((ws.title, ws) for ws in workbook_master.worksheets)

    #df.to_excel(writer,sheet_name='Banknifty',startrow=workbook_master['Banknifty'].max_row,startcol=0,header=False,index=False)

    #writer.save()
    #writer.close()

    #with pd.ExcelWriter(filename,engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:  
    #    writer.sheets = dict((ws.title, ws) for ws in writer.worksheets)
    #    df.to_excel(writer, sheet_name='Banknifty')
    time.sleep(60)
    if(loopcount==2):
        df_concat= pd.DataFrame()
        #for df_index in df:
        df_concat = pd.concat(df)

        book = xw.Book("D:\Python_Trader_Code\All_Expiries.xlsx")
        sheet = book.sheets("Banknifty")
        sheet.range("A1").value=df_concat

        exit()

    #initial_range = sheet.range("A1").vertical.last_cell
    #sheet.range(initial_range.row+1)
