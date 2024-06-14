import pandas as pd
import numpy as np

data = {'38046':
{'2024-01-31T15:08:47':{'tt':'2024-01-31T15:08:47','ltp':118.6,'Tsym':'NIFTY01FEB24C21750','openi':2901800.0,'pdopeni':'2610050','Volume':'71953900'},
'2024-01-31T15:08:48': {'tt': '2024-01-31T15:08:48','ltp':113.6,'Tsym':'NIFTY01FEB24C21750','openi':560180.0,'pdopeni':'210050','Volume':'51953900'}, 
'2024-01-31T15:08:49': {'tt': '2024-01-31T15:08:49','ltp':122.6,'Tsym':'NIFTY01FEB24C21750','openi':2980.0,'pdopeni':'210050','Volume':'51953900'},
'2024-01-31T15:08:50': {'tt': '2024-01-31T15:08:50','ltp':115.6,'Tsym':'NIFTY01FEB24C21750','openi':290180.0,'pdopeni':'210050','Volume':'71953900'},
'2024-01-31T15:08:51': {'tt': '2024-01-31T15:08:51','ltp':119.6,'Tsym':'NIFTY01FEB24C21750','openi':2909980.0,'pdopeni':'210050','Volume':'51953900'},
'2024-01-31T15:08:52': {'tt': '2024-01-31T15:08:52','ltp':111.6,'Tsym':'NIFTY01FEB24C21750','openi':290180.0,'pdopeni':'210050','Volume':'51953900'},
'2024-01-31T15:08:53': {'tt': '2024-01-31T15:08:53','ltp':118.6,'Tsym':'NIFTY01FEB24C21750','openi':290180.0,'pdopeni':'210050','Volume':'51953900'}},
'38000':
{'2024-01-31T15:10:47':{'tt':'2024-01-31T15:10:47','ltp':118.6,'Tsym':'NIFTY01FEB24C21750','openi':2901800.0,'pdopeni':'2610050','Volume':'71953900'},
'2024-01-31T15:10:48': {'tt': '2024-01-31T15:10:48','ltp':113.6,'Tsym':'NIFTY01FEB24C21750','openi':560180.0,'pdopeni':'210050','Volume':'51953900'}, 
'2024-01-31T15:10:49': {'tt': '2024-01-31T15:10:49','ltp':122.6,'Tsym':'NIFTY01FEB24C21750','openi':2980.0,'pdopeni':'210050','Volume':'51953900'},
'2024-01-31T15:10:50': {'tt': '2024-01-31T15:10:50','ltp':115.6,'Tsym':'NIFTY01FEB24C21750','openi':290180.0,'pdopeni':'210050','Volume':'71953900'},
'2024-01-31T15:10:51': {'tt': '2024-01-31T15:10:51','ltp':119.6,'Tsym':'NIFTY01FEB24C21750','openi':2909980.0,'pdopeni':'210050','Volume':'51953900'},
'2024-01-31T15:10:52': {'tt': '2024-01-31T15:10:52','ltp':111.6,'Tsym':'NIFTY01FEB24C21750','openi':290180.0,'pdopeni':'210050','Volume':'51953900'},
'2024-01-31T15:10:53': {'tt': '2024-01-31T15:10:53','ltp':118.6,'Tsym':'NIFTY01FEB24C21750','openi':290180.0,'pdopeni':'210050','Volume':'51953900'}}}

def convert_to_ohlc_create_file(data):
    if data is not None:
        df = pd.DataFrame.from_dict({(i, j): data[i][j]
                                            for i in data.keys()
                                            for j in data[i].keys()},
                                            orient='index')
        #resample_LTP = data['LTP'].resample('15Min').ohlc(_method='ohlc')

        for idx,data in df.groupby(level=0):
            df_level_zero = df.xs(idx, level=0)
            print(df_level_zero)

        print(type(df.Volume))
        df['tt'] = pd.to_datetime(df['tt'])
        df = df.set_index('tt')
        df['Volume']= df['Volume'].astype(int)
        df = df.resample('1min').apply(agg_ohlcv)
        df = df.ffill()
        print(df)
def agg_ohlcv(x):
    arr = x['ltp'].values
    names = {
        'low': min(arr) if len(arr) > 0 else np.nan,
        'high': max(arr) if len(arr) > 0 else np.nan,
        'open': arr[0] if len(arr) > 0 else np.nan,
        'close': arr[-1] if len(arr) > 0 else np.nan,
        'Volume': sum(x['Volume'].values) if len(x['Volume'].values) > 0 else 0
    }
    return pd.Series(names)


#print(df.loc[['38000']['2024-01-31T15:10:47']])