#https://www.youtube.com/watch?v=E7d0PxLB5hQ
#https://drive.google.com/drive/folders/1IzKWxRUaBd30oRdB9GJ1qUO-Ot_Pi0Je
#https://github.com/5paisa/py5paisa/blob/11f402a7ac66882440ae15695a7d4956572bbfb2/py5paisa/strategy.py
#https://zerodha.com/varsity/module/option-strategies/

import numpy as np
import pandas as pd
import requests
import logging
#logging.basicConfig(level= logging.DEBUG)
#logger= logging.getLogger(__name__)

from login import userid, susertoken
from ShoonyaApi import ShoonyaApi
from utils import *

#NIFTY50:   RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK, HINDUNILVR
#BANKNIFTY: HDFCBANK, ICICIBANK, KOTAKBANK, AXISBANK, SBIN

#io
#aa
#oi

def closest(lst, K):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i]- K))]

class strategies:
    def __init__(self, exchange=None, symbol=None):
        self.shoonya= ShoonyaApi(userid, susertoken)
        self.exchange=exchange
        self.symbol=symbol
        self.oed=utils.get_oed(self.exchange, self.symbol)
        self.fed=utils.get_fed(self.exchange, self.symbol)
        self.lot_size=utils.get_lot_size(self.exchange, self.symbol)

    def place_order(self, direction, ts, quantity, lot_size):  #MKT
        print(f'#in place_order: direction:{direction}, ts:{ts}, quantity:{quantity* lot_size}')
        response= self.shoonya.place_order(
            buy_or_sell='B' if direction== 'B' else 'S',
            product_type='M',
            exchange=self.exchange,
            tradingsymbol=ts,
            quantity=int(quantity* lot_size), #MLot
            discloseqty=0,
            price_type='MKT',
            price=0.0,
            trigger_price=None,
            retention='DAY',
            remarks=None)
        print(f'#=== response: {response}\n');

        if response!= None and 'Ok' in response['stat']:
            print(f"#order_placed with status: {response['stat']}")
            return response['norenordno']
        return None

    #bullish option strategies ===
    def bull_call(self): pass
    def sell_put(self): pass

    #long call spread or debit call spread;
    def bull_call_spread(self):
        #strategy:
        #Buy 1 ATM call option (leg 1)
        #Sell 1 OTM call option (leg 2)

        print(f'\n#=== Algo started (bull_call_spread)...@{datetime.now()}')
        strike= self.shoonya.get_atm_strike(self.exchange, self.fed)

        ltp= self.shoonya.get_ltp(self.exchange, self.fed)
        strike= utils.get_nearest_strike(self.exchange, self.symbol, ltp)

        long_call= f'{self.oed}C{strike}'
        long_call_premium= self.shoonya.get_ltp(self.exchange, long_call)
        print(f'# {long_call} -  {long_call_premium}')

        short_call_otm= f'{self.oed}C{strike+ 100}'
        print(short_call_otm)

        short_call_otm_premium= self.shoonya.get_ltp(self.exchange, short_call_otm)
        print(f'# {short_call_otm} -  {short_call_otm_premium}')

        #net_premium= short_call_otm_premium- long_call_premium
        #print(f'#net_premium: {net_premium}')

        #order_id1= self.place_order('B', long_call, 1, self.lot_size))
        #order_id2= self.place_order('S', short_call_otm, 1, self.lot_size))

    #short put spread or credit put spread;
    def bull_put_spread(self):
        #strategy:
        #Buy 1 OTM Put option (leg 1)
        #Sell 1 ITM Put option (leg 2)

        print(f'\n#=== Algo started (bull_put_spread)...@{datetime.now()}')
        strike= self.shoonya.get_atm_strike(self.exchange, self.fed)

        long_put_otm= f'{self.oed}P{strike- 100}'
        long_put_otm_premium= self.shoonya.get_ltp(self.exchange, long_put_otm)
        print(f'# {long_put_otm} -  {long_put_otm_premium}')

        short_put_itm= f'{self.oed}P{strike+ 100}'
        short_put_itm_premium= self.shoonya.get_ltp(self.exchange, short_put_itm)
        print(f'# {short_put_itm} -  {short_put_itm_premium}')

        #self.place_order('B', long_put_otm, 1, self.lot_size)
        #self.place_order('S', short_put_itm, 1, self.lot_size)

    #Call Ratio Back Spread
    def call_ratio_back_spread(self):
        #strategy:
        #Buy 2 OTM Call option (leg1)
        #Sell 1 ITM Call option (leg2)

        print(f'\n#=== Algo started (call_ratio_back_spread)...@{datetime.now()}')
        strike= self.shoonya.get_atm_strike(self.exchange, self.fed)

        long_call_otm= f'{self.oed}C{strike+ 100}'
        long_call_otm_premium= self.shoonya.get_ltp(self.exchange, long_call_otm)
        print(f'# {long_call_otm} -  {long_call_otm_premium}')

        short_call_itm= f'{self.oed}C{strike- 100}'
        short_call_itm_premium= self.shoonya.get_ltp(self.exchange, short_call_itm)
        print(f'# {short_call_itm} -  {short_call_itm_premium}')

        #order_id1= self.place_order('B', long_call_otm, 2, self.lot_size))
        #order_id2= self.place_order('S', short_call_itm, 1, self.lot_size))

    #bearish option strategy ====
    def buy_put(self): pass
    def sell_call(self): pass

    #debit put spread or long put spread
    def bear_put_spread(self):
        #strategy:
        #Buy 1 ITM Put option (leg1)
        #Sell 1 OTM Put option (leg2)

        print(f'\n#=== Algo started (bear_put_spread)...@{datetime.now()}')
        strike= self.shoonya.get_atm_strike(self.exchange, self.fed)

        long_put_itm= f'{self.oed}P{strike+ 100}'
        long_put_itm_premium= self.shoonya.get_ltp(self.exchange, long_put_itm)
        print(f'# {long_put_itm} -  {long_put_itm_premium}')

        short_put_otm= f'{self.oed}P{strike- 100}'
        short_put_otm_premium= self.shoonya.get_ltp(self.exchange, short_put_otm)
        print(f'# {short_put_otm} -  {short_put_otm_premium}')

        #order_id1= self.place_order('B', long_put_itm, 1, self.lot_size))
        #order_id2= self.place_order('S', short_put_otm, 1, self.lot_size))

    #
    def bear_call_spread(self):
        #strategy:
        #Buy 1 OTM Call option (leg 1)
        #Sell 1 ITM Call option (leg 2)

        print(f'\n#=== Algo started (bear_call_spread)...@{datetime.now()}')
        strike= self.shoonya.get_atm_strike(self.exchange, self.fed)

        long_call_otm= f'{self.oed}C{strike+ 100}'
        long_call_otm_premium= self.shoonya.get_ltp(self.exchange, long_call_otm)
        print(f'# {long_call_otm} -  {long_call_otm_premium}')

        short_call_itm= f'{self.oed}C{strike- 100}'
        short_call_itm_premium= self.shoonya.get_ltp(self.exchange, short_call_itm)
        print(f'# {short_call_itm} -  {short_call_itm_premium}')

        #order_id1= self.place_order('B', long_call_otm, 1, self.lot_size)
        #order_id2= self.place_order('S', short_call_itm, 1, self.lot_size)

    #
    def put_ratio_back_spread(self):
        #strategy:
        #Buy 2 OTM Put option (leg 1)
        #Sell 1 ITM Put option (leg 2)

        print(f'\n#=== Algo started (put_ratio_back_spread)...@{datetime.now()}')
        strike= self.shoonya.get_atm_strike(self.exchange, self.fed)

        long_put_otm= f'{self.oed}P{strike- 100}'
        long_put_otm_premium= self.shoonya.get_ltp(self.exchange, long_put_otm)
        print(f'# {long_put_otm} -  {long_put_otm_premium}')

        short_put_itm= f'{self.oed}P{strike+ 100}'
        short_put_itm_premium= self.shoonya.get_ltp(self.exchange, short_put_itm)
        print(f'# {short_put_itm} -  {short_put_itm_premium}')

        #order_id1= self.place_order('B', long_put_otm, 2, self.lot_size)
        #order_id2= self.place_order('S', short_put_itm, 1, self.lot_size)

    #neutral ===
    def short_straddle(self):
        print(f'\n#=== Algo started (short_straddle)...@{datetime.now()}')
        strike= self.shoonya.get_atm_strike(self.exchange, self.fed)

        short_call= f'{self.oed}C{strike}'
        short_call_premium= self.shoonya.get_ltp(self.exchange, short_call)
        print(f'# {short_call} -  {short_call_premium}')

        short_put= f'{self.oed}P{strike}'
        short_put_premium= self.shoonya.get_ltp(self.exchange, short_put)
        print(f'# {short_put} -  {short_put_premium}')

        for i in [short_call, short_put]:
            print(self.place_order('S', i, 1, self.lot_size))

    def iron_butterfly(self): pass
    def short_strangle(self): pass
    def short_iron_condor(self): pass

    #others ===
    def iron_fly(self):
        #strategy:
        #Sell 1 Call option     (leg1)
        #Sell 1 Put option      (leg2)
        #Buy 1 OTM Call option  (leg3)
        #Buy 1 OTM Put option   (leg4)

        lst= [100, 200, 300, 400, 500, 600, 700, 800, 900]
        print(f'\n#=== Algo started (iron_fly)...@{datetime.now()}')
        strike= self.shoonya.get_atm_strike(self.exchange, self.fed)

        short_call= f'{self.oed}C{strike}'
        short_call_premium= self.shoonya.get_ltp(self.exchange, short_call)
        print(f'# {short_call} -  {short_call_premium}')

        short_put= f'{self.oed}P{strike}'
        short_put_premium= self.shoonya.get_ltp(self.exchange, short_put)
        print(f'# {short_put} -  {short_put_premium}')

        cp= short_call_premium+ short_put_premium
        nearest= closest(lst, cp)
        print(f'#cp: {cp}, nearest: {nearest}')

        long_call_otm= f'{self.oed}C{strike+ nearest}'
        long_call_otm_premium= self.shoonya.get_ltp(self.exchange, long_call_otm)
        print(f'# {long_call_otm} -  {long_call_otm_premium}')

        long_put_otm= f'{self.oed}P{strike- nearest}'
        long_put_otm_premium= self.shoonya.get_ltp(self.exchange, long_put_otm)
        print(f'# {long_put_otm} -  {long_put_otm_premium}')

        #for i in [long_call_otm, long_put_otm]: order_id[i]= self.place_order('B', i, 1, self.lot_size)

        #for i in [short_put, short_call]: order_id[i]= self.place_order('S', i, 1, self.lot_size)

#================================================
s= strategies('NFO', 'NMDC')

s.bull_call_spread()
#s.bull_put_spread()
#s.call_ratio_back_spread()

#s.bear_put_spread()
#s.bear_call_spread()
#s.put_ratio_back_spread()

#s.short_straddle()
#s.long_straddle()

#s.iron_fly()



