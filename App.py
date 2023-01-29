import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import time # to simulate a real time data, time loop 
import plotly.express as px # interactive charts 
from ChartInk_Scaper_FileWatcher_Processor import processnewfiles
from ChartInk_Scrape_With_Multiprocess import screenmapper
import requests

def removefirstcolumn(dataframeinput):
    first_column = dataframeinput.columns[0]
    # Delete first
    dataframeinput = dataframeinput.drop([first_column], axis=1)
    return dataframeinput

def ProcessNewFiles():
    pass
   
    




st.set_page_config(
    page_title = 'Real-Time ChartInk Screener Dashboard',
    page_icon = '✅',
    layout = 'wide'
)

# dashboard title

st.title("Real-Time ChartInk Screener Dashboard")

# top-level filters 
screenertypes= []

for item in screenmapper.items():

    screenertypes.append(item[1])

screener_filter = st.selectbox("Select the type of screener", screenertypes)


# creating a single-element container.
placeholder = st.empty()


import pandas as pd
from datetime import datetime
import streamlit as st
import pandas as pd 
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

from ChartInk_Scrape_With_Multiprocess import screenmapper

if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

dfs=[]

df_1=pd.DataFrame(columns=['sr','nsecode','name','bsecode','per_chg','close','volume','ScreenerName','TimeOfDay'])
df_2=pd.DataFrame(columns=['sr','nsecode','name','bsecode','per_chg','close','volume','ScreenerName','TimeOfDay'])

from ChartInk_Scrape_With_Multiprocess import screenmapper


uploaded_file = st.file_uploader("Choose a file(Bullish)")
if uploaded_file is not None:
    df_bullish = pd.read_csv(uploaded_file)


uploaded_file_1 = st.file_uploader("Choose a file(Bearish)")
if uploaded_file_1 is not None:
    df_bearish = pd.read_csv(uploaded_file_1)

uploaded_file_2 = st.file_uploader("Choose a file(intradayBearish)")
if uploaded_file_2 is not None:
    df_intraday_bearish = pd.read_csv(uploaded_file_2)

uploaded_file_3 = st.file_uploader("Choose a file(intradayBullish)")
if uploaded_file_3 is not None:
    df_intraday_bullish = pd.read_csv(uploaded_file_3)

uploaded_file_4 = st.file_uploader("Choose a file(mostlovedscreeners)")
if uploaded_file_4 is not None:
    df_most_loved_screeners = pd.read_csv(uploaded_file_4)

optionMaxOccurence=30
result='bearish-screeners'

optionMaxOccurence = st.selectbox(
    'Maximum occurence of the stocks in screeners',
     [5,40,35,30,25,20,15,10])

actions = {'A': 'bullish-screeners', 'B': 'intraday-bullish-screeners', 'C': 'bearish-screeners', 'D':'intraday-bearish-screeners'}

optionMktDirection = st.selectbox('Choose one:', ['_', 'bullish-screeners', 'intraday-bullish-screeners', 'bearish-screeners','intraday-bearish-screeners','most-loved-screeners'],label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,key='marketDirection')

if optionMktDirection != '_':
    result = optionMktDirection #(f'You chose {choice}')   

with open('style.css')as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

#for key,value in 

df_bullish['OccurInDiffScreeners'] = df_bullish.groupby(by="nsecode")['nsecode'].transform('count')
df_bullish = df_bullish.query(f'OccurInDiffScreeners >{optionMaxOccurence}')
df_bullish.drop(['Unnamed: 0','sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
grp_bullish =  df_bullish.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
grp_bullish = grp_bullish[grp_bullish['OccurInDiffScreeners'] >optionMaxOccurence].sort_values(['OccurInDiffScreeners'],ascending=False)
#print(grp.head(10))

df_bearish['OccurInDiffScreeners'] = df_bearish.groupby(by="nsecode")['nsecode'].transform('count')
df_bearish = df_bearish.query(f'OccurInDiffScreeners >{optionMaxOccurence}')
df_bearish.drop(['Unnamed: 0','sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
grp_bearish =  df_bearish.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
grp_bearish = grp_bearish[grp_bearish['OccurInDiffScreeners'] >optionMaxOccurence].sort_values(['OccurInDiffScreeners'],ascending=False)
#print(grp.head(10))

df_intraday_bearish['OccurInDiffScreeners'] = df_intraday_bearish.groupby(by="nsecode")['nsecode'].transform('count')
df_intraday_bearish = df_intraday_bearish.query(f'OccurInDiffScreeners >{optionMaxOccurence}')
df_intraday_bearish.drop(['Unnamed: 0','sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
grp_intraday_bearish =  df_intraday_bearish.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
grp_intraday_bearish = grp_intraday_bearish[grp_intraday_bearish['OccurInDiffScreeners'] >optionMaxOccurence].sort_values(['OccurInDiffScreeners'],ascending=False)

df_intraday_bullish['OccurInDiffScreeners'] = df_intraday_bullish.groupby(by="nsecode")['nsecode'].transform('count')
df_intraday_bullish = df_intraday_bullish.query(f'OccurInDiffScreeners >{optionMaxOccurence}')
df_intraday_bullish.drop(['Unnamed: 0','sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
grp_intraday_bullish =  df_intraday_bullish.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
grp_intraday_bullish = grp_intraday_bullish[grp_intraday_bullish['OccurInDiffScreeners'] >optionMaxOccurence].sort_values(['OccurInDiffScreeners'],ascending=False)

df_most_loved_screeners['OccurInDiffScreeners'] = df_bullish.groupby(by="nsecode")['nsecode'].transform('count')
df_most_loved_screeners = df_most_loved_screeners.query(f'OccurInDiffScreeners >{optionMaxOccurence}')
df_most_loved_screeners.drop(['Unnamed: 0','sr','per_chg','close','bsecode','volume'],axis=1,inplace=True)
grp_most_loved_screeners =  df_most_loved_screeners.groupby("nsecode",as_index=False)['OccurInDiffScreeners'].max() 
grp_most_loved_screeners = grp_most_loved_screeners[grp_most_loved_screeners['OccurInDiffScreeners'] >optionMaxOccurence].sort_values(['OccurInDiffScreeners'],ascending=False)

if optionMktDirection == "bullish-screeners":
    df = grp_bullish
elif optionMktDirection == "intraday-bullish-screeners":
    df = grp_intraday_bullish
elif optionMktDirection == "intraday-bearish-screeners":
    df = grp_intraday_bearish
elif optionMktDirection == "bearish-screeners":
    df = grp_bearish
else:
    df = grp_most_loved_screeners

placeholder = st.empty()

if df.empty != True:
    with placeholder.container():
    #while True:
        kpi1, kpi2, kpi3,kpi4,kpi5 = st.columns(5)

            # fill in those three columns with respective metrics or KPIs 
        if df.iloc[0].empty == False:
            kpi1.metric(label="Top-Most Stock⏳", value=df.iloc[0]['nsecode'])
        if df.iloc[1].empty == False:
            kpi2.metric(label="Second Top Most Stock 💍", value=df.iloc[1]['nsecode'])
        if df.iloc[2].empty == False:
            kpi3.metric(label="Third Top Most Stock 💍", value=df.iloc[2]['nsecode'])
        if df.iloc[3].empty == False:
            kpi4.metric(label="Fourth Top Most Stock＄", value=df.iloc[3]['nsecode'])
        if df.iloc[4].empty == False:
                kpi5.metric(label="Fifth Top Most Stock＄", value=df.iloc[4]['nsecode']) 

        AgGrid(df.head(15))
        #time.sleep(60)



