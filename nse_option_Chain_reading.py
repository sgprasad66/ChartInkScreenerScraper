import requests
import pandas as pd

sesi=requests.Session()
headers={}
headers['user-agent']='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
a=sesi.get("https://www.nseindia.com/",headers=headers)

indices = ['BANKNIFTY','FINNIFTY','NIFTY']

def FetchOptionChainfromNSE (scrip):
    
    if scrip in indices:
        url=f"https://www.nseindia.com/api/option-chain-indices?symbol={scrip}"
    else:
        symbol4NSE = scrip.replace('&', '%26')
        url=f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol4NSE}"
    
    a=sesi.get(url,headers=headers)
    return a.json()['records']
	
def GetOptionChain(name, expiry):
    option_chain = pd.DataFrame()
    option_chain_record = FetchOptionChainfromNSE (name)
    option_chain_data = option_chain_record['data']
    option_chain_data_df = pd.DataFrame(option_chain_data)
    option_chain_data_df  = option_chain_data_df[(option_chain_data_df.expiryDate == expiry) ]
    
    OptionChain_CE = pd.DataFrame()
    OptionChain_CE['CE'] = option_chain_data_df['CE']
    
    OptionChain_CE_expand = pd.concat([OptionChain_CE.drop(['CE'], axis=1), OptionChain_CE['CE'].apply(pd.Series)], axis=1)

    OptionChain_PE = pd.DataFrame()
    OptionChain_PE['PE'] = option_chain_data_df['PE']
    OptionChain_PE_expand = pd.concat([OptionChain_PE.drop(['PE'], axis=1), OptionChain_PE['PE'].apply(pd.Series)], axis=1)
    
    option_chain['CE_OI'] =  OptionChain_CE_expand['openInterest']
    option_chain['CE_CHNG_IN_OI'] =  OptionChain_CE_expand['changeinOpenInterest']
    option_chain['CE_VOLUME'] =  OptionChain_CE_expand['totalTradedVolume']
    option_chain['CE_IV'] =  OptionChain_CE_expand['impliedVolatility']
    option_chain['CE_LTP'] =  OptionChain_CE_expand['lastPrice']
    option_chain['CE_CHNG'] =  OptionChain_CE_expand['change']
    option_chain['CE_BID_QTY'] =  OptionChain_CE_expand['bidQty']
    option_chain['CE_BID_PRICE'] =  OptionChain_CE_expand['bidprice']
    option_chain['CE_ASK_PRICE'] =  OptionChain_CE_expand['askPrice']
    option_chain['CE_ASK_QTY'] =  OptionChain_CE_expand['askQty']
    
    option_chain['strikePrice'] =  option_chain_data_df['strikePrice']
    
    option_chain['PE_BID_QTY'] =  OptionChain_PE_expand['bidQty']
    option_chain['PE_BID_PRICE'] =  OptionChain_PE_expand['bidprice']
    option_chain['PE_ASK_PRICE'] =  OptionChain_PE_expand['askPrice']
    option_chain['PE_ASK_QTY'] =  OptionChain_PE_expand['askQty']
    option_chain['PE_CHNG'] =  OptionChain_PE_expand['change']
    option_chain['PE_LTP'] =  OptionChain_PE_expand['lastPrice']
    option_chain['PE_IV'] =  OptionChain_PE_expand['impliedVolatility']
    option_chain['PE_VOLUME'] =  OptionChain_PE_expand['totalTradedVolume']
    option_chain['PE_CHNG_IN_OI'] =  OptionChain_PE_expand['changeinOpenInterest']
    option_chain['PE_OI'] =  OptionChain_PE_expand['openInterest']
    
    return option_chain
	
scripname = 'TCS'
ExpiryDate = '29-Sep-2022'
Option_chain = GetOptionChain(scripname, ExpiryDate)
Option_chain.to_csv(scripname + ".csv", index=False)