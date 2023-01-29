from kite_trade import *
import pandas as pd


user_id = ""       # Login Id
password = ""      # Login password
twofa = ""         # Login Pin or TOTP

user_id = 'HC9926'
password= 'Murthy12#'
twofa='885470'

#enctoken = get_enctoken(user_id, password, twofa)
#kite = KiteApp(enctoken=enctoken)

#enctoken = "zIHb6tJAjlPNKlWePko2v4RKCp8G9kKll4X5KTeGx16/xMjPb2pieapxQUxdmxZ8NaPiZhv3LQscrvFfpHb5wujmx3H+TNRW430TliWs/NHlwo10Vd+ywQ=="
enctoken = "MI5dzBfv41e6h+xyoycfuC7jz2XpTI7KRK4Ps7PipO0V2k1UhWNZY6htvI0gvdUmmUUbwHxnw8zgF00kp6uo3jSZhQR0bqeXlEmsP5EIgPq4fPviRugsGg=="
kite = KiteApp(enctoken=enctoken)

#print(kite.margins())
#print(kite.baskets())

ff = print(kite.instruments())
#print(kite.instruments("NSE"))
#print(kite.instruments("NFO"))

# Get Live Data
#print(kite.ltp("NSE:RELIANCE"))
#print(kite.ltp(["NSE:NIFTY 50", "NSE:NIFTY BANK"]))
print(kite.quote(["NSE:NIFTY BANK", "NSE:ACC", "NFO:NIFTY22SEPFUT"]))

import datetime
instrument_token = 9604354
from_datetime = datetime.datetime.now() - datetime.timedelta(days=7)     # From last & days
to_datetime = datetime.datetime.now()
interval = "5minute"
#print(kite.historical_data(instrument_token, from_datetime, to_datetime, interval, continuous=False, oi=False))


# Place Order
order = kite.place_order(variety=kite.VARIETY_REGULAR,
                         exchange=kite.EXCHANGE_NSE,
                         tradingsymbol="ACC",
                         transaction_type=kite.TRANSACTION_TYPE_BUY,
                         quantity=1,
                         product=kite.PRODUCT_CNC,
                         order_type=kite.ORDER_TYPE_MARKET,
                         price=None,
                         validity=None,
                         disclosed_quantity=None,
                         trigger_price=None,
                         squareoff=None,
                         stoploss=None,
                         trailing_stoploss=None,
                         tag="TradeViaPython")

print(order)

# Modify order
kite.modify_order(variety=kite.VARIETY_REGULAR,
                  order_id="order_id",
                  parent_order_id=None,
                  quantity=5,
                  price=200,
                  order_type=kite.ORDER_TYPE_LIMIT,
                  trigger_price=None,
                  validity=kite.VALIDITY_DAY,
                  disclosed_quantity=None)

# Cancel order
kite.cancel_order(variety=kite.VARIETY_REGULAR,
                  order_id="order_id",
                  parent_order_id=None)