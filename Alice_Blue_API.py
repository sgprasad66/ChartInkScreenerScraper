from pya3 import *

alice = Aliceblue(user_id='AB067538',api_key='3NCsUCE9N4NIJvfGC4SM7Lof1yHvbaKfCxTkzHnnFzQThjHJjT6rvOTadBBWp7ZYbAJDF34FAkWGuySHfHl3eEfEeXENGQInKg99TNz0UU6Fa41lud8JbOi9mOGlNoKm')

print(alice.get_session_id())

bn_call = alice.get_instrument_for_fno(exch="NFO",symbol = 'BANKNIFTY', expiry_date="2023-01-12", is_fut=False, strike=42000, is_CE = True)
bn_put = alice.get_instrument_for_fno(exch="NFO",symbol = 'BANKNIFTY', expiry_date="2023-01-12", is_fut=False, strike=44000, is_CE = False)

print(alice.get_balance()) # get balance / margin limitsr
print(alice.get_profile()) # get profile
print(alice.get_daywise_positions()) # get daywise positions
print(alice.get_netwise_positions()) # get all netwise positions
print(alice.get_holding_positions()) # get holding positions


alice.get_contract_master("MCX")
alice.get_contract_master("NFO")
alice.get_contract_master("NSE")
alice.get_contract_master("BSE")
alice.get_contract_master("CDS")
alice.get_contract_master("BFO")
alice.get_contract_master("INDICES")

print(alice.get_instrument_by_symbol('NSE','ONGC'))
print(alice.get_instrument_by_symbol('BSE','TATASTEEL'))
print(alice.get_instrument_by_symbol('MCX','GOLDM'))
print(alice.get_instrument_by_symbol('INDICES','NIFTY 50'))
print(alice.get_instrument_by_symbol('INDICES','NIFTY BANK'))

print(alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date="2023-01-26", is_fut=False,strike=42000, is_CE=True))
print(alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date="2023-01-26", is_fut=False,strike=44000, is_CE=False))

print(alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date="2023-01-26", is_fut=False,strike=42000, is_CE=False))
print(alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date="2023-01-26", is_fut=False,strike=44000, is_CE=True))

''' print(alice.get_instrument_for_fno(exch="NFO",symbol='BANKNIFTY', expiry_date="2022-09-04", is_fut=False,strike=37700, is_CE=True))
print(alice.get_instrument_for_fno(exch="CDS",symbol='USDINR', expiry_date="2022-09-16", is_fut=True,strike=None, is_CE=False))
print(alice.get_instrument_for_fno(exch="CDS",symbol='USDINR', expiry_date="2022-09-23", is_fut=False,strike=79.50000, is_CE=False))
print(alice.get_instrument_for_fno(exch="CDS",symbol='USDINR', expiry_date="2022-09-28", is_fut=False,strike=79.50000, is_CE=True)) '''