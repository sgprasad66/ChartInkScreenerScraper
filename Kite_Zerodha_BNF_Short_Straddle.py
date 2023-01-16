import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta, TH
from kiteconnect import KiteConnect


def get_kite():
    kiteObj = KiteConnect(api_key='API_KEY')
    kiteObj.set_access_token('ACCESS_TOKEN')
    return kiteObj


kite = get_kite()
instrumentsList = None


def getCMP(tradingSymbol):
    quote = kite.quote(tradingSymbol)
    if quote:
        return quote[tradingSymbol]['last_price']
    else:
        return 0


def get_symbols(expiry, name, strike, ins_type):
    global instrumentsList

    if instrumentsList is None:
        instrumentsList = kite.instruments('NFO')

    lst_b = [num for num in instrumentsList if num['expiry'] == expiry and num['strike'] == strike
             and num['instrument_type'] == ins_type and num['name'] == name]
    return lst_b[0]['tradingsymbol']


def place_order(tradingSymbol, price, qty, direction, exchangeType, product, orderType):
    try:
        orderId = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=exchangeType,
            tradingsymbol=tradingSymbol,
            transaction_type=direction,
            quantity=qty,
            price=price,
            product=product,
            order_type=orderType)

        logging.info('Order placed successfully, orderId = %s', orderId)
        return orderId
    except Exception as e:
        logging.info('Order placement failed: %s', e.message)


if __name__ == '__main__':
    # Find ATM Strike of Nifty
    atm_strike = round(getCMP('NSE:NIFTY 50'), -2)

    next_thursday_expiry = datetime.today() + relativedelta(weekday=TH(1))

    symbol_ce = get_symbols(next_thursday_expiry.date(), 'NIFTY', atm_strike, 'CE')
    symbol_pe = get_symbols(next_thursday_expiry.date(), 'NIFTY', atm_strike, 'PE')

    place_order(symbol_ce, 0, 50, kite.TRANSACTION_TYPE_SELL, KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
                KiteConnect.ORDER_TYPE_MARKET)

    place_order(symbol_pe, 0, 50, kite.TRANSACTION_TYPE_SELL, KiteConnect.EXCHANGE_NFO, KiteConnect.PRODUCT_MIS,
                KiteConnect.ORDER_TYPE_MARKET) 