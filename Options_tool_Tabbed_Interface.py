#!/usr/bin/env python
import configparser
import numpy as np
import random
import string
import operator
import matplotlib
import datetime
import time
import json
import pandas as pd
import PySimpleGUI as sg
from random import randint
from bson import json_util
from matplotlib import style
from datetime import datetime
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Alice_Blue_API import calculate_mtm,get_traded_records
import Utils
from Utils import read_ini_file,create_gui,write_ini_file,decide_persistence_mechanism

sg.theme('DarkBlue')
style.use("ggplot")
checked = b'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'
unchecked = b'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'
time_mtm_dict={}   
mtm=0.0
g_mtm=0.0
capital=0.0
current_capital=0.0
returns=0.0
config=None
#code for plotting the graph
fig = Figure(figsize=(4, 2), dpi=100)

ax = fig.gca()
tradeddate=''
eventcount=0
NUM_DATAPOINTS=10800
xList=[]
yList=[]

telegram_count=0
matplotlib.use("TkAgg")

backdays=5
optionMaxOccurence=5
df_bull=pd.DataFrame()
df_bear=pd.DataFrame()
df_intrabull=pd.DataFrame()
df_intrabear=pd.DataFrame()


def removefirstcolumn(dataframeinput):
    first_column = dataframeinput.columns[0]
    # Delete first
    dataframeinput = dataframeinput.drop([first_column], axis=1)
    return dataframeinput

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

    if days == '' or days == None:
        days=1

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

def oncombochange():
    global df_bull
    global df_bear
    global df_intrabull
    global df_intrabear

    df_bull=pd.DataFrame()
    df_bear=pd.DataFrame()  
    df_intrabull=pd.DataFrame()
    df_intrabear=pd.DataFrame()

    bullish,bearish,intradaybullish,intradaybearish=process(backdays)
    if bullish.empty == False:
        df_bull = convertdataframe(bullish)
    if bearish.empty == False:
        df_bear = convertdataframe(bearish)
    if intradaybullish.empty == False:
        df_intrabull = convertdataframe(intradaybullish)
    if intradaybearish.empty == False:
        df_intrabear = convertdataframe(intradaybearish)
    df_bull.to_csv("bull.csv",index=False)
    df_bear.to_csv("bear.csv",index=False)
    df_intrabull.to_csv("intrabull.csv",index=False)
    df_intrabear.to_csv("intrabear.csv",index=False)
    print("intrabear.csv")


def convertdataframe(df):
    #if df is not None :
    if df.empty == False:
        df['OccurInDiffScreeners'] = df.groupby(by="nsecode")['nsecode'].transform('count')
        df = df.query(f'OccurInDiffScreeners >{optionMaxOccurence}')
        df.drop(['sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
        grp_bullish =  df.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
        grp_bullish = grp_bullish[grp_bullish['OccurInDiffScreeners'] >optionMaxOccurence].sort_values(['OccurInDiffScreeners'],ascending=False)
        return   grp_bullish
Dayslist = [day for day in np.arange(1,60,1)]



def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


def animate(i):
    import matplotlib.ticker as ticker
    global a
    global xList
    global yList
    pullData = open("D:\FilesFromRoopesh\OptionsPakshiResampling\PySimpleGUI\DemoPrograms\sampleText.txt","r").read()
    dataList = pullData.split('\n')
    import random
    time_val={}
    
    xList = xList[-50:]
    yList = yList[-50:]

    a.set_xticks(np.arange(xList[0], len(xList)+1, 10))

        
        #a.set_xticks([])
    a.set_yticks(np.arange(1,len(yList)+1,50))
    a.set_xlim(xList[0],xList[49])
    a.set_ylim(0,300)

    a.clear()
    a.plot(xList, yList)

    a.xaxis.set_major_locator(ticker.NullLocator())
    a.yaxis.set_major_locator(ticker.NullLocator())

import requests
TelegramBotCredential = '6106136909:AAEWKu4Xk1QtoIjMnoZzblRdc5SZdcntOTY'
ReceiverTelegramID='5416986599'

def send_to_telegram(message):

    apiURL = f'https://api.telegram.org/bot{TelegramBotCredential}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': ReceiverTelegramID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)

send_to_telegram("Hello from Python!")
def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    try:
        draw_figure.canvas_packed.pop(figure_agg.get_tk_widget())
    except Exception as e:
        print(f'Error removing {figure_agg} from list', e)

def pydt_remove_cols(DT, *rmcols):
    return DT[:, f[:].remove([f[col] for col in rmcols])]

ini_file_path = "D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\configurations.ini"  # Replace with your actual .ini file path

# The tab 1, 2, 3 layouts - what goes inside the tab
# ------ Make the Table Data ------

while True:
    try:
        repo = Utils.decide_persistence_mechanism()
        data = repo.get_traded_records()
        if not len(data) ==0:
            break
    except Exception as e:
        print("The file is not accessible for now..retrying")
        time.sleep(5)

if len(data) == 0:
    sg.popup_no_frame("No records for the day")
else:
    dict_data = data #eval(data)
    df_dict = pd.DataFrame(dict_data)
    data = df_dict[df_dict['TradingSymbol'].str.contains("BANKNIFTY")]  #if 'BANKNIFTY' in row['TradingSymbol']:
    
    headings = ['TradingSymbol','OrderId','Qty','Ltp','OrderType','TpHit',
                'SlHit','FinalPrice','ProductType','TradedDate','FinalTradedDate','Strike','Expiry','Mtm-Profit-Loss','Capital']
    
    data.drop(['StrategyId', 'IsHedged'], axis=1, inplace=True)
    traded_data = data
    

from datetime import date
from datetime import timedelta
today = date.today()
Dateslist = [(today - timedelta(days = day)).strftime("%d_%m_%Y") for day in range(360)]
 
frame_layout = [[sg.T('Choose either of the chechboxes to only view BankNifty and/or Stock(cash) Positions-:')],
                    [sg.Image(checked, key=('-IMAGE-', 1), metadata=True, enable_events=True),sg.Text("BankNifty"),
                     sg.Image(unchecked, key=('-IMAGE-', 2), metadata=False, enable_events=True),sg.Text("Cash Stocks")]]

tab2_layout = [[sg.Frame('View BankNifty or Cash Trades', frame_layout, font='Any 12', title_color='blue')],
                    [sg.Text('Select date for which to view the trades:'),sg.Combo(values=Dateslist,
                     size=(20, 7),
                     enable_events=True,
                     key="-COMBOBOX-",font="Helvetica 12",
                     metadata=[]),
                     sg.Text('Total Records found ===>'),sg.Text(key='-COUNT-')],
                    [sg.Image(unchecked, key=('-CUMULATIVE-'), metadata=False, enable_events=True),sg.Text("Selected Date P&L or Cumulative P&L")],
                    [sg.Table(values=traded_data.values.tolist(), headings = headings,auto_size_columns=True,
                        display_row_numbers=False,
                        justification='center',
                        right_click_selects=True,
                        max_col_width=25,
                        col_widths=10, #list(map(lambda x:len(x)+1, headings)),
                        vertical_scroll_only = False, 
                        num_rows=min(25, len(data)),
                        key='-TABLE-',
                        selected_row_colors='red on yellow',
                        enable_events=True,
                        expand_x=True,
                        expand_y=True,                        #enable_click_events=True,           # Comment out to not enable header and other clicks
                        tooltip='This table displays the current trading positions')],
                    [sg.Canvas(key="-CANVAS-")],
                    [sg.Button('Plot MTM in Real-time graph',key='-GRAPH-'), sg.Button('Change Theme',key='-CHANGETHEME-')],
                    [sg.Text('MTM position for the day:'),sg.Text(key='-MTM-'),
                     sg.Text('Capital Deployed for the day:'),sg.Text(key='-CAPITAL-'),
                     sg.Text('Capital in Trade:'),sg.Text(key='-CURRENTCAPITAL-'),
                      sg.Text('Returns for the day:'),sg.Text(key='-RETURNS-'), sg.T(k='-CLICKED-')]]

tab1_layout = [create_gui(read_ini_file(ini_file_path))]
layouttop = [sg.Text('How many days of BackTracked Data to Display:'),sg.Combo(values=Dayslist,
                     size=(20, 7),
                     enable_events=True,
                     key="-COMBOBOXCOUNT-",font="Helvetica 12",
                     metadata=[]),sg.Button("Get Data",key='-GETDATA-'),sg.Button("Graphical View",key='-GETDATAGRAPH-')
                     ]

layouttoprow = [sg.Text("Bullish Scrips    ======>  "),sg.Table(values=df_bull.values.tolist(), headings=['NseCode','NumberOfOccurencesinScreeners'],auto_size_columns=False,
                        display_row_numbers=False,
                        justification='center',
                        right_click_selects=True,
                        max_col_width=10,
                        col_widths=10, #list(map(lambda x:len(x)+1, headings)),
                        vertical_scroll_only = False, 
                        alternating_row_color='DarkGreen',
                        num_rows=15,
                        key='-TABLE-BULL-',
                        selected_row_colors='red on yellow',
                        enable_events=True,
                        expand_x=True,
                        expand_y=True,
                        enable_click_events=True,           # Comment out to not enable header and other clicks
                        tooltip='This table displays the bullish count'),sg.Canvas(key='-CANVAS1-'),
                    sg.Text("Bearish Scrips  =======> "),sg.Table(values=df_bear.values.tolist(), headings=['NseCode','NumberOfOccurencesinScreeners'],auto_size_columns=False,
                        display_row_numbers=False,
                        justification='center',
                        right_click_selects=True,
                        max_col_width=10,
                        col_widths=10, #list(map(lambda x:len(x)+1, headings)),
                        vertical_scroll_only = False, 
                        alternating_row_color='DarkRed',
                        num_rows=15,
                        key='-TABLE-BEAR-',
                        selected_row_colors='red on yellow',
                        enable_events=True,
                        expand_x=True,
                        expand_y=True,
                        enable_click_events=True,           # Comment out to not enable header and other clicks
                        tooltip='This table displays the bearish count')
                ]
layoutbottomrow =   [sg.Text("IntraDay Bullish Scrips==>"),
                        sg.Table(values=df_intrabull.values.tolist(), headings=['NseCode','NumberOfOccurencesinScreeners'],auto_size_columns=False,
                        display_row_numbers=False,
                        justification='center',
                        right_click_selects=True,
                        max_col_width=10,
                        col_widths=10, #list(map(lambda x:len(x)+1, headings)),
                        vertical_scroll_only = False, 
                        alternating_row_color='LightGreen',
                        num_rows=15,
                        key='-TABLE-INTRABULL-',
                        selected_row_colors='red on yellow',
                        enable_events=True,
                        expand_x=True,
                        expand_y=True,
                        enable_click_events=True,           # Comment out to not enable header and other clicks
                        tooltip='This table displays the bullish count'),
                        sg.Text("IntraDay Bearish Scrips ==> "),
                    sg.Table(values=df_intrabear.values.tolist(), headings=['NseCode','NumberOfOccurencesinScreeners'],auto_size_columns=False,
                        display_row_numbers=False,
                        justification='center',
                        right_click_selects=True,
                        max_col_width=10,
                        col_widths=10, #list(map(lambda x:len(x)+1, headings)),
                        vertical_scroll_only = False, 
                        alternating_row_color='Red',
                        num_rows=15,
                        key='-TABLE-INTRABEAR-',
                        selected_row_colors='red on yellow',
                        enable_events=True,
                        expand_x=True,
                        expand_y=True,
                        enable_click_events=True,           # Comment out to not enable header and other clicks
                        tooltip='This table displays the bearish count')
                ]

layout_scrip_count = [layouttop,layouttoprow,layoutbottomrow]
tab3_layout = layout_scrip_count #[[sg.Text('Tab 3')]]
tab4_layout = [[sg.Canvas(key="-CANVAS-")],
                     [sg.Button('Start ChartInk Scraper Process',key='-Start-ChartInk-Scraper-')],
                     [sg.Button('Execute Market Pre-open Script',key='-Execute-Preopen-Script-')],
                     [sg.Button('Execute End-of-day Script',key='-Execute-Postmarket-Script-')],
                     [sg.Button('Execute File Watcher Script',key='-Execute-Filewatcher-Script-')],
                     [sg.Text('MTM position for the Strategy:'),sg.Text(key='-MTM-'), sg.T(k='-CLICKED-')]]

# The TabgGroup layout - it must contain only Tabs
tab_group_layout = [[sg.Tab('Global Settings for the Trading App', tab1_layout, key='-TAB1-'),
                     sg.Tab('Trades/Positions for Nifty/BankNifty/Finnifty/Midcpnifty', tab2_layout, visible=True, key='-TAB2-'),
                     sg.Tab('Scrip Counts for Intraday', tab3_layout,visible=True, key='-TAB3-'),
                     sg.Tab('Processes to Execute', tab4_layout, visible=True, key='-TAB4-')]]

# The window layout - defines the entire window
layout = [[sg.TabGroup(tab_group_layout,
                       enable_events=True,
                       key='-TABGROUP-',pad=(10, 10),size=(2200,1750))]]

window = sg.Window('Options Trading Tool', layout,
                    resizable=True, right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT, finalize=True,font='Helvetica 13', sbar_background_color='green',
                    size=(2200,1750))

window.maximize()
listbox = window["-COMBOBOX-"]
# Add the ability to double-click a cell
window["-TABLE-"].bind('<Double-Button-1>' , "+-double click-")
print(window[('-IMAGE-',1)].metadata)
print(window[('-IMAGE-',2)].metadata)

canvas_elem = window['-CANVAS-']
canvas = canvas_elem.TKCanvas
fig_agg = draw_figure(canvas,fig)

tab_keys = ('-TAB1-','-TAB2-','-TAB3-', '-TAB4-')         # map from an input value to a key
# ------ Event Loop ------
while True:
    event, values = window.read(timeout=2000)
    #if event == '-CANVAS-+-double click-':
    #ani = animation.FuncAnimation(fig, animate, interval=20000)
    #fig_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)
    if ~df_bull.empty:
            window['-TABLE-BULL-'].update(values=df_bull.values.tolist())
    
    if ~df_bear.empty:
        window['-TABLE-BEAR-'].update(values=df_bear.values.tolist())

    if ~df_intrabull.empty:
        window['-TABLE-INTRABULL-'].update(values=df_intrabull.values.tolist())

    if ~df_intrabear.empty:
        window['-TABLE-INTRABEAR-'].update(values=df_intrabear.values.tolist())

   
    if event == sg.TIMEOUT_EVENT and values['-TABGROUP-'] == '-TAB1-':
        ini_file_path = "D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\configurations.ini"  # Replace with your actual .ini file path
        config = read_ini_file(ini_file_path)

        tab1_layout = create_gui(config)
    if event == '-Save-':
        print(values)
        ini_file_path = "D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\configurations.ini"
        write_ini_file(ini_file_path,config,values)
        
    if event == sg.TIMEOUT_EVENT and values['-TABGROUP-'] == '-TAB2-':
        import pandas as pd
        time_component = datetime.today().strftime("%H%M%S")
        
        def get_mtm(row):
            g_mtm=0.0
            mtm=0.0
            if row['OrderType'] == 'BUY':
                mtm = (row['FinalPrice']-row['Ltp'])*row['Qty']
            else:
                mtm = (row['Ltp']-row['FinalPrice'])*row['Qty']
            g_mtm = g_mtm+mtm
            return round(mtm,2)
        def get_capital(row):
            cap=0.0
            capital=0.0
            #if row[]()
            if row['OrderType'] == 'BUY':
                cap = (row['Ltp'])*row['Qty']
            else:
                cap = (row['Ltp'])*row['Qty']
            capital = capital+cap
            return round(cap,2)
        tradeddate=values['-COMBOBOX-']
        
        if tradeddate == '':
            tradeddate=datetime.today().strftime("%d_%m_%Y")
                
        if not window['-CUMULATIVE-'].metadata:
            data = Utils.decide_persistence_mechanism().get_traded_records()
        else:
            data = Utils.decide_persistence_mechanism().get_historical_traded_records()
        
        dict_data = data #eval(data)
        df = pd.DataFrame(dict_data)
        telegram_count += 1
        if df.empty is True:
            #sg.popup_non_blocking("No records found for the day")
            window['-TABLE-'].update(values=[])
            window['-COUNT-'].update(str(0))
            window['-MTM-'].update(str(0))
            window['-CAPITAL-'].update(str(0))
            window['-CURRENTCAPITAL-'].update(str(0))
        else:
        
            if window[('-IMAGE-',1)].metadata & ~window[('-IMAGE-',2)].metadata:
                df = df[df['TradingSymbol'].str.contains("BANKNIFTY")] 
            elif window[('-IMAGE-',2)].metadata & ~window[('-IMAGE-',1)].metadata:
                df = df[~df['TradingSymbol'].str.contains("BANKNIFTY")] 
            
            
            window['-COUNT-'].update(str(df.shape[0]))
            df['Mtm-Profit-Loss'] = df.apply(get_mtm,axis=1)
            df['Capital'] = df.apply(get_capital,axis=1)
            headings = ['TradingSymbol','OrderId','Qty','Ltp','OrderType','TpHit','SlHit','FinalPrice','ProductType','TradedDate','FinalTradedDate','Strike','Expiry','Mtm-Profit-Loss','Capital']
            df.drop(['StrategyId', 'IsHedged'], axis=1, inplace=True)
            df.reset_index(drop=True,inplace=True)

            print(df.head(25))
            rownum=0
            mtm=0.0
            capital = 0.0
            tuplelist =[]
            for index,row in df.iterrows():
                tuplecolor=(index,'white','Blue')
                if (row['SlHit'] == True):# or row['Mtm'] <0.0):
                    tuplecolor=(index,'white','DeepPink4')
                    current_capital = capital-row['Capital']
                elif row['TpHit'] == True:# or row['Mtm'] >= 0.0:
                    tuplecolor=(index,'black','LightGreen')
                    current_capital = capital-row['Capital']
                else:
                    tuplecolor=(index,'black','Cyan')
                    pass
                tuplelist.append(tuplecolor)

                mtm = row['Mtm-Profit-Loss']+mtm
                capital = row['Capital']+capital
            listOfTuples = tuple(tuplelist)
                
            
            if mtm > 0.0:
                window['-MTM-'].update(background_color='LightGreen',text_color='black')
            else:
                window['-MTM-'].update(background_color='DeepPink4',text_color='white')
            window['-CAPITAL-'].update(background_color='yellow',text_color='black')
            window['-CAPITAL-'].update((format(capital,'.2f')))

            window['-CURRENTCAPITAL-'].update(background_color='cyan',text_color='black')
            curr_cap = capital-current_capital
            window['-CURRENTCAPITAL-'].update((format(curr_cap,'.2f')))

            returns=0.0
            if capital == 0.0:
                returns = 0.0
            else:
                returns = (mtm/capital)*100

            if returns > 0.0:
                window['-RETURNS-'].update(background_color='LightGreen',text_color='black')
            else:
                window['-RETURNS-'].update(background_color='DeepPink4',text_color='black')
            window['-RETURNS-'].update((format(returns,'.2f')))
            #time_mtm_dict[time_component] = randint(-2000, 5000)
            time_mtm_dict[time_component] = mtm
            window['-MTM-'].update((format(mtm,'.2f')))
            if telegram_count % 90 == 0:
                send_to_telegram(format(mtm,'.2f'))
            data=df.values.tolist()
            window['-TABLE-'].update(values=df.values.tolist())
            window['-TABLE-'].update(row_colors=listOfTuples)
            window['-CANVAS-'].update()
            data_points = 50

            if ax and len(time_mtm_dict) > 50:
                last50values=[]
                ax.clear()
                for x in list(time_mtm_dict)[-50:]:
                    print(x)
                    last50values.append(time_mtm_dict[x])
                print(last50values)
                ax.plot(range(data_points), last50values,  color='purple')
                fig_agg.draw()


    print(event, values)
    if event == '-COMBOBOX-':
        tradeddate=values['-COMBOBOX-']
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'Edit Me':
        sg.execute_editor(__file__)
    elif event == 'Version':
        sg.popup_scrolled(__file__, sg.get_versions(), location=window.current_location(), keep_on_top=True, non_blocking=True)
    elif event == 'Change Colors':
        import subprocess                                                                                                                                                                   
        subprocess.call("python D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\Config_chartinkscraper.py")
        #subprocess.call("python D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\Alice_Blue_API.py") 
        from subprocess import Popen, PIPE
        process = Popen(['python', 'D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\Alice_Blue_API.py'], stdout=None, stderr=None)

    elif event== '-GRAPH-': 

        fig = Figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel("X axis")
        ax.set_ylabel("Y axis")
        ax.grid()
        fig_agg = draw_figure(canvas, fig)
        # make a bunch of random data points
        dpts = [randint(-2000, 5000) for x in range(NUM_DATAPOINTS)]

    
        time_component = datetime.today().strftime("%H%M%S")
        time_mtm_dict[time_component]   = mtm
        event, values = window.read(timeout=1000)
        if event in ('Exit', None):
            exit(69)
        #slider_elem.update(i)       # slider shows "progress" through the data points
        ax.cla()                    # clear the subplot
        ax.grid()                   # draw the grid
        data_points = 50
        ax.plot(range(data_points), dpts[-50:],  color='purple',background='black')
        fig_agg.draw()

    elif event == '-CHANGETHEME-':
        sg.theme('DarkGreen')
        window['-TABLE-'].update()

    if event[0] in ('-IMAGE-', '-TEXT-'):
        cbox_key = ('-IMAGE-', event[1])
        text_key = ('-TEXT-', event[1])
        window[cbox_key].metadata = not window[cbox_key].metadata
        window[cbox_key].update(checked if window[cbox_key].metadata else unchecked)
    
    if event == '-CUMULATIVE-':
        window['-CUMULATIVE-'].metadata = not window['-CUMULATIVE-'].metadata
        window['-CUMULATIVE-'].update(checked if window['-CUMULATIVE-'].metadata else unchecked)
        if window['-CUMULATIVE-'].metadata:
            try:
                repo = Utils.decide_persistence_mechanism()
                traded_data = repo.get_historical_traded_records()
                window['-TABLE-'].update(values=traded_data.values.tolist())
            except Exception as e:
                print("The file is not accessible for now..retrying")
                time.sleep(5)

    if event == '-TABLE-':
        #print('Row {} Column {}'.format(values['-TABLE-'][0], values['-TABLE-'][1]))
        if len(values['-TABLE-']) > 0:
            selected_row_index = values['-TABLE-'][0]
            sg.popup(data[selected_row_index][5])
            print(selected_row_index)
    #if event == 
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'Edit Me':
        sg.execute_editor(__file__)
    elif event == 'Version':
        sg.popup_scrolled(__file__, sg.get_versions(), location=window.current_location(), keep_on_top=True, non_blocking=True)
    if event == 'Double':
        for i in range(1, len(data)):
            data.append(data[i])
        window['-TABLE-'].update(values=data[1:][:])
    elif event == 'Change Colors':
        window['-TABLE-'].update(row_colors=((8, 'white', 'deeppink4'), (9, 'green')))
       
        import subprocess                                                                                                                                                                   
        #subprocess.call("python D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\Config_chartinkscraper.py")
        #subprocess.call("python D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\Alice_Blue_API.py") 
        from subprocess import Popen, PIPE
        #process = Popen(['python', 'D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\Alice_Blue_API.py'], stdout=None, stderr=None)
       #short_straddle_main()
       #df = calculate_mtm()
        sp = sg.execute_command_subprocess("python D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\ChartInk_Scaper_FileWatcher_Processor.py")
        # This will cause the program to wait for the subprocess to finish
        print(sg.execute_get_results(sp)[0])
        
    elif event == '-TABLE-+-double click-':
        print('Last cell clicked was', window['-TABLE-'].get_last_clicked_position())
        if isinstance(event, tuple):
        # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
        # You can also call Table.get_last_clicked_position to get the cell clicked
            if event[0] == '-TABLE-':
                if event[2][0] == -1 and event[2][1] != -1:           # Header was clicked and wasn't the "row" column
                    col_num_clicked = event[2][1]
                    #new_table = sort_table(data[1:][:],(col_num_clicked, 0))
                    window['-TABLE-'].update(new_table)
                    data = [data[0]] + new_table
                window['-CLICKED-'].update(f'{event[2][0]},{event[2][1]}')

    elif event == '-COMBOBOXCOUNT-':
            backdays=values['-COMBOBOXCOUNT-']
    elif event == '-GETDATA-':
        backdays=values['-COMBOBOXCOUNT-']
        oncombochange()
        if ~df_bull.empty:
            window['-TABLE-BULL-'].update(values=df_bull.values.tolist())
        if ~df_bear.empty:
            window['-TABLE-BEAR-'].update(values=df_bear.values.tolist())
        if ~df_intrabull.empty:
            window['-TABLE-INTRABULL-'].update(values=df_intrabull.values.tolist())
        if ~df_intrabear.empty:
            window['-TABLE-INTRABEAR-'].update(values=df_intrabear.values.tolist())

        ''' window['-TABLE-BULL-'].update(row_colors='green')
        window['-TABLE-INTRABULL-'].update(row_colors='green')
        window['-TABLE-BEAR-'].update(row_colors='deeppink4')
        window['-TABLE-INTRABEAR-'].update(row_colors='deeppink4') '''
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if event == '-GETDATAGRAPH-':
        if ~df_bull.empty :
            window['-CANVAS1-'].update(values=df_bull.value_counts().plot.bar())
    if event == 'Edit Me':
        sg.execute_editor(__file__)
    elif event == 'Version':
        sg.popup_scrolled(__file__, sg.get_versions(), location=window.current_location(), keep_on_top=True, non_blocking=True)
    #fig.
window.close()

def handle_global_settings_tab_click():
    pass



