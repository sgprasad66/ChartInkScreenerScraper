import PySimpleGUI as sg
import pandas as pd
import numpy as np
#from datetime import datetime
#import sys

backdays=5
optionMaxOccurence=15
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
    #df1=None 
    #df2=None
    #df3=None
    #df4=None
    df1=pd.DataFrame()
    df2=pd.DataFrame()
    df3=pd.DataFrame()
    df4=pd.DataFrame()
    path = "D:\\FilesFromRoopesh\\OptionsPakshiResampling\\ChartInkScreenerScraper\\"
    #path="Z:\ChartInk_Scraped_Files\\"
    todayfolder = datetime.datetime.today().strftime("%d_%m_%Y")
    if backdays <= 1:
        dates.append(todayfolder)
    else:
        for index in range(0,backdays):
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
#backdays=4  


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
    

def convertdataframe(df):
    #if df is not None :
    if df.empty == False:
        df['OccurInDiffScreeners'] = df.groupby(by="nsecode")['nsecode'].transform('count')
        df = df.query(f'OccurInDiffScreeners >{optionMaxOccurence}')
        df.drop(['sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
        grp_bullish =  df.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
        grp_bullish = grp_bullish[grp_bullish['OccurInDiffScreeners'] >optionMaxOccurence].sort_values(['OccurInDiffScreeners'],ascending=False)
        return   grp_bullish




Dateslist = [day for day in np.arange(1,60,1)]

layouttop = [[sg.Text('How many days of BackTracked Data to Display:'),sg.Combo(values=Dateslist,
                     size=(20, 7),
                     enable_events=True,
                     key="-COMBOBOX-",font="Helvetica 12",
                     metadata=[]),sg.Button("Get Data",key='-GETDATA-'),sg.Button("Graphical View",key='-GETDATAGRAPH-')
                     ]]

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

layout = [layouttop,layouttoprow,layoutbottomrow]

    # ------ Create Window ------
window = sg.Window('The Table Element', layout,
                        resizable=True, right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT, finalize=True,font="Helvetica 12")

while True:
    event, values = window.read(timeout=2000)
    if event == sg.TIMEOUT_EVENT:
        #print(event, values)
        
        if ~df_bull.empty:
            window['-TABLE-BULL-'].update(values=df_bull.values.tolist())
    
        if ~df_bear.empty:
            window['-TABLE-BEAR-'].update(values=df_bear.values.tolist())
    
        if ~df_intrabull.empty:
            window['-TABLE-INTRABULL-'].update(values=df_intrabull.values.tolist())
    
        if ~df_intrabear.empty:
            window['-TABLE-INTRABEAR-'].update(values=df_intrabear.values.tolist())
        
        #pass
    elif event == '-COMBOBOX-':
        backdays=values['-COMBOBOX-']
    elif event == '-GETDATA-':
        backdays=values['-COMBOBOX-']
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
        window['-TABLE-BEAR-'].update(row_colors='red')
        window['-TABLE-INTRABEAR-'].update(row_colors='red') '''
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if event == '-GETDATAGRAPH-':
        if ~df_bull.empty :
            window['-CANVAS1-'].update(values=df_bull.value_counts().plot.bar())
    if event == 'Edit Me':
        sg.execute_editor(__file__)
    elif event == 'Version':
        sg.popup_scrolled(__file__, sg.get_versions(), location=window.current_location(), keep_on_top=True, non_blocking=True)
    
window.close()