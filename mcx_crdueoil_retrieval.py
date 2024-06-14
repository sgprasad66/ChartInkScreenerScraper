''' import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    if 'MarketData' in data:
        market_data = data['MarketData']
        if 'Commodity' in market_data and market_data['Commodity'] == 'CRUDEOILM':
            if 'Contracts' in market_data and len(market_data['Contracts']) > 0:
                latest_price = market_data['Contracts'][0]['Price']
                print("Latest Crude Oil price:", latest_price)

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws):
    print("WebSocket closed")

def on_open(ws):
    # Subscribe to crude oil market data
    subscription_message = {
        "MessageType": "Subscribe",
        "MarketDataRequest": {
            "Exchange": "MCX",
            "Commodity": "CRUDEOILM"
        }
    }
    ws.send(json.dumps(subscription_message))

if __name__ == "__main__":
    websocket_url = "wss://example.com"  # Update with the actual MCX websocket URL

    # Create and configure the websocket connection
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(websocket_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open

    # Run the websocket connection
    ws.run_forever()
 

from alice_blue import AliceBlue
from alice_blue import LiveFeedType
import datetime
import time
import os
from pya3 import *
import helper
from datetime import datetime
global alice
config = helper.read_config()

mongodbclient = config['MongoDBSettings']['mongodbclient']
databasename = config['MongoDBSettings']['databasename']
collectionname = config['MongoDBSettings']['collectionname']
deletecollectionname=config['MongoDBSettings']['deletecollectionname']
enctoken=config['KiteSettings']['enctoken']
aliceblueusername=config['AliceBlueSettings']['username']
aliceblueapikey=config['AliceBlueSettings']['apikey']

log_filename_path =config['Logger']['LogFilePath']
log_file_Name=config['Logger']['LogFileName']
# user_name = "x"
# password = "x"
# two_fa = "x"
# api_secret_key = "x"

def get_alice():
    global alice
    alice = Aliceblue(user_id=aliceblueusername,api_key=aliceblueapikey)
    print(alice.get_session_id())
    return alice

#with open("D:\\Algo_Trading\\_Trading_\\Access_Token.txt", "r") as f:
#    access_token = f.read().strip()
#alice = AliceBlue(username=user_name, password=password, access_token=access_token)
get_alice()
socket_opened = False
token = ""
open_price = 0
high_price = 0
low_price = 0
close_price = 0

def event_handler_quote_update(message):
    # print(f"quote update {message}")
    global token
    global open_price
    global high_price
    global low_price
    global close_price

    token = message['token']
    open_price = message['open']
    high_price = message['high']
    low_price = message['low']
    close_price = message['close']

    LTP = 0
    socket_opened = False
    subscribe_flag = False
    subscribe_list = []
    unsubscribe_list = []

def socket_open():  # Socket open callback function
    print("Connected")
    global socket_opened
    socket_opened = True
    if subscribe_flag:  # This is used to resubscribe the script when reconnect the socket.
        alice.subscribe(subscribe_list)

def socket_close():  # On Socket close this callback function will trigger
    global socket_opened, LTP
    socket_opened = False
    LTP = 0
    print("Closed")

def socket_error(message):  # Socket Error Message will receive in this callback function
    global LTP
    LTP = 0
    print("Error :", message)

def feed_data(message):  # Socket feed data will receive in this callback function
    global LTP, subscribe_flag
    feed_message = json.loads(message)
    if feed_message["t"] == "ck":
        print("Connection Acknowledgement status :%s (Websocket Connected)" % feed_message["s"])
        subscribe_flag = True
        print("subscribe_flag :", subscribe_flag)
        print("-------------------------------------------------------------------------------")
        pass
    elif feed_message["t"] == "tk":
        print("Token Acknowledgement status :%s " % feed_message)
        print("-------------------------------------------------------------------------------")
        pass
    else:
        print("Feed :", feed_message)
        LTP = feed_message[
            'lp'] if 'lp' in feed_message else LTP  # If LTP in the response it will store in LTP variable

# Socket Connection Request
alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                      socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True,market_depth=False)

while not socket_opened:
    pass
i = alice.get_instrument_for_fno('CRUDEOIL', datetime.date(2023,7,19).strftime("%Y-%m-%d"), is_fut=True, exchange='MCX')
token_crude = '252453.0'
t = alice.get_instrument_by_token(exchange='MCX', token=token_crude)
subscribe_list = [alice.get_instrument_by_symbol(exchange='MCX', symbol='CRUDEOIL 19JUL23 FUT')]
alice.subscribe(subscribe_list)
print(datetime.now())
sleep(10)
print(datetime.now())
# unsubscribe_list = [alice.get_instrument_by_symbol("NSE", "RELIANCE")]
# alice.unsubscribe(unsubscribe_list)
# sleep(8)

# Stop the websocket
alice.stop_websocket()
sleep(10)
print(datetime.now())

# Connect the socket after socket close
alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                      socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)
                      

import subprocess
import PySimpleGUI as sg

def launch_script(script_path):
    try:
        subprocess.Popen(["python", script_path])
    except Exception as e:
        print(f"Error launching script: {e}")

def main():
    layout = [
        [sg.Text("Click the button to launch a script:")],
        [sg.Button("Scrip_Count_Display"), sg.Button("Finvasia_Get_Strike_From_Given_Premium"),sg.Button("Open_Positions_Today_UI")],
        [sg.Button("Pause", key="pause"), sg.Button("Exit")]
    ]

    window = sg.Window("Script Runner", layout)

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Exit"):
            break
        elif event.startswith("Scrip"):
            script_number = int(event.split()[-1])
            script_path = f"Scrip_Count_Display.py"  # Adjust the paths to your actual scripts
            launch_script(script_path)
        elif event.startswith('Finvasia'):
            launch_script('Finvasia_Get_Strike_From_Given_Premium.py')
        elif event.startswith('Open'):
            launch_script('Open_Positions_Today_UI.py')
        elif event == "pause":
            # Put your pause logic here (e.g., time.sleep(300) for 5 minutes)
            pass

    window.close()

if __name__ == "__main__":
    main()'''

import configparser
import PySimpleGUI as sg

def read_ini_file(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

def create_gui(config):
    layout = []
    for section in config.sections():
        layout.append([sg.Text(f"[{section}]")])
        for key in config[section]:
            layout.append([sg.Text(key), sg.InputText(default_text=config[section][key], key=key)])

    layout.append([sg.Button("Save")])
    return sg.Window("INI File Editor", layout)

def main():
    ini_file_path = "configurations.ini"  # Replace with your actual .ini file path
    config = read_ini_file(ini_file_path)

    window = create_gui(config)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Save":
            for section in config.sections():
                for key in config[section]:
                    config[section][key] = values[key]

            with open(ini_file_path, "w") as config_file:
                config.write(config_file)

    window.close()

if __name__ == "__main__":
    main()
