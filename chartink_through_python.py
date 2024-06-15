def GetDataFromChartink(payload):

    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
    import logging
    from win10toast import ToastNotifier
    #toast = ToastNotifier()
    #toast.show_toast("Hello, World!")
    
    Charting_Link = "https://chartink.com/screener/"
    Charting_url = 'https://chartink.com/screener/process'

    payload = {'scan_clause': payload}
    
    try:

        with requests.Session() as s:
            r = s.get(Charting_Link)
            soup = BeautifulSoup(r.text, "html.parser")
            csrf = soup.select_one("[name='csrf-token']")['content']
            s.headers['x-csrf-token'] = csrf
            #headers={}
            s.headers['Content-Type']='application/x-www-form-urlencoded'
            r = s.post(Charting_url, data=payload)

            df = pd.DataFrame()
            for item in r.json()['data']:
                df = df.append(item, ignore_index=True)
        return df
    except requests.exceptions.HTTPError as e:
        #print(e)
        logging.info(e)
        #print("some error in the connection")
        logging.info("Error in network connection")
    except requests.exceptions.RequestException as e:
        #print(e)
        logging.info(e)

# Python code to remove whitespace
from functools import reduce

#Function to remove white space
def removespaces(txt):
	#return reduce(lambda x, y: (x+y) if (y != " ") else x, string, "");
    import re

    res = re.sub('  ([\(]) ?',r'\1', txt)  #re.sub(' +', ' ', str)
    res = re.sub(' ([\(]) ?',r'\1', res)
    s = res
    return s


	
# Python3 code to demonstrate working of
# remove additional space from string
# Using re.sub()


def CreateCsvFile(marketdirection,starttime,ohlc_data):
    from pathlib import Path
    from datetime import datetime
    
    today = datetime.now().strftime("%d_%m_%Y")
    endtime=datetime.now().strftime("%H_%M_%S")
    if ohlc_data == True:
        filename = today+"\\ohlc_data\\"+starttime+"_"+marketdirection+"_"+endtime+".csv"
    else:
        filename = today+"\\"+starttime+"_"+marketdirection+"_"+endtime+".csv"
    output_file = Path(filename)
       
    output_file.parent.mkdir(exist_ok=True, parents=True)
    return output_file
    


def ChartInkScraper(marketdirection):

    import pandas as pd
    from datetime import datetime
    from selenium import webdriver
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver import DesiredCapabilities as dc
    import pyperclip
    import logging
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    #from webdriver_manager.chrome import ChromeDriverManager


    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    service = Service(r"C:\\chromedriver.exe")
    options = webdriver.ChromeOptions()

    #uncomment below to run chrome in headless mode
    #options.add_argument("--headless=new")
    
    driver = webdriver.Chrome(service=service, options=options)


    dc.CHROME["unexpectedAlertBehaviour"] = "accept"
    driver.get("https://chartink.com/screeners/"+marketdirection)
    listOfDataFramesOuter = pd.DataFrame()
    
    try:

        starttime=datetime.now().strftime("%H_%M_%S")
        num_rows = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//table[@class='table table-striped']")))
        elements = num_rows.find_elements(By.TAG_NAME, 'tr')
        listofhyperlinks=[]
        screenercount=0
        logging.info("Inside ChartInkScraper")
        for e in elements:
            linktext = e.text.split('\n')[0]
            listofhyperlinks.append(linktext)
        
        for hypertext in listofhyperlinks:
            element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.LINK_TEXT, hypertext)))
            element.click()
            element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//div[@class='atlas-heading']"))) 
    
            screenercount=screenercount+1
            #print(screenercount)
            logging.info(screenercount)
            #toast = toast.ToastNotifier()
            #toast.show_toast(screenercount)
            #print("--"+hypertext)
            logging.info("--"+hypertext)
            # Get all the elements available with tag name 'i'
            elements = element.find_elements(By.TAG_NAME, 'i')
            for e in elements:
                #print(e.accessible_name)
                e.click()
        
            #print(pyperclip.paste())
            payloaddata = pyperclip.paste()

            #payloaddata='( {33489} ( latest ema( close,20 ) > 20 and latest sma( volume,20 ) >= 100000 and latest ichimoku conversion line( 3,7,14 ) >= latest ichimoku base line( 3,7,14 ) and latest ichimoku span a( 3,7,14 ) >= latest ichimoku span b( 3,7,14 ) and latest close >= latest ichimoku cloud bottom( 3,7,14 ) and( {33489} ( latest close >= latest parabolic sar( 0.02,0.02,0.2 ) and latest rsi( 10 ) >= 20 and latest stochrsi( 10 ) >= 20 and latest cci( 10 ) >= 0 and latest mfi( 10 ) >= 20 and latest williams %r( 10 ) >= -80 and latest close >= latest ema( close,14 ) and latest adx di positive( 10 ) >= latest adx di negative( 10 ) and latest aroon up( 10 ) >= latest aroon down( 10 ) and latest slow stochastic %k( 5,3 ) >= latest slow stochastic %d( 5,3 ) and latest fast stochastic %k( 5,3 ) >= latest fast stochastic %d( 5,3 ) and latest close >= latest sma( close,10 ) ) ) and ( {33489} ( latest macd line( 14,5,3 ) >= latest macd signal( 14,5,3 ) and latest macd histogram( 14,5,3 ) >= 0 ) ) and ( {33489} ( latest rsi( 14 ) > 50 and latest stochrsi( 14 ) > 50 and latest rsi( 10 ) < 80 and latest close >= latest upper bollinger band( 20,2 ) and latest close >= latest ichimoku cloud bottom( 9,26,52 ) and latest close > latest open and latest volume > 100000 and latest ema( close,5 ) > latest ema( close,20 ) and latest ema( close,20 ) > latest ema( close,50 ) and latest close > latest ema( close,50 ) ) ) ) ) '
            payloaddata = removespaces(payloaddata)

            try:
                driver.switch_to.alert.dismiss()
            except Exception:
                #print('No alert present')
                logging.info("No alert present")
            
            data = GetDataFromChartink(payloaddata)
            if data is not None:
        
                if data.empty == False:
                    data = data.sort_values(by='per_chg', ascending=False)
                
                data['ScreenerName'] = hypertext
                data['TimeOfDay'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                #print(data.info())
                if data.shape[1] != 2:
                    data['nsecode']=data['nsecode'].astype('string')
            
                #toast.show_toast(data)
                if listOfDataFramesOuter.empty == True:
                    listOfDataFramesOuter = data
                else:
                    if data.empty == False:
                        listOfDataFramesOuter = pd.concat([listOfDataFramesOuter,data])

                driver.back()

        formattedfilepath = CreateCsvFile(marketdirection,starttime,False)
        listOfDataFramesOuter.to_csv(formattedfilepath)
    finally:
        driver.quit()


