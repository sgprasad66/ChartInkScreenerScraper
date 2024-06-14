
#from Finvasia_Get_Strike_From_Given_Premium import options_Buy_ATM_Call_Sell_Deep_OTM_Calls,ShoonyaApiPy,init,options_short_straddle
from Finvasia_Get_Strike_From_Given_Premium import finvasia_trading_helper
import threading
import time
if __name__ == "__main__":
    #fth = finvasia_trading_helper()

    #thread_process = threading.Thread(target=fth.process_messages, args=(fth.trading_message_queue,))
    #thread_process.daemon = True
    #thread_process.start()
        
        #fth.post_messages("1,NSE:Nifty Bank,P,B")
    #finvasia_trading_helper.post_messages("5,NSE:BEL,C")
    #finvasia_trading_helper.post_messages("1,NSE:BEL,C,B")
    finvasia_trading_helper.post_messages("1,NSE:Nifty,P,B")
    finvasia_trading_helper.post_messages("3,NSE:JINDALSTEL,C")
    #finvasia_trading_helper.post_messages("1,NSE:BSOFT,C,B")
    #finvasia_trading_helper.post_messages("3,NSE:HAL,C")
    #finvasia_trading_helper.post_messages("5,NSE:VEDL,C")
    #finvasia_trading_helper.post_messages("1,NSE:NAUKRI,C")
    #finvasia_trading_helper.post_messages("1,NSE:Nifty,C,B")
    #finvasia_trading_helper.post_messages("1,NSE:Nifty Bank,P,B")
    #finvasia_trading_helper.post_messages("1,NSE:Nifty Bank,P,B")
    #finvasia_trading_helper.post_messages("1,NSE:Nifty Bank,P,B")
    
    #finvasia_trading_helper.post_messages("2,NSE:Nifty,P,C")
    #fth.post_messages("1,NSE:BHARATFORG,C,B")
    time.sleep(65)
        #fth.post_messages("1,NSE:SBIN,C,B")
    #3options_buy_index_stock("NSE:SRF","P","B")
    #options_buy_index_stock("NSE:SBIN","C","B")
    #options_buy_index_stock("NSE:PFC","C","B")
    #options_buy_index_stock("NSE:CHAMBLFERT","C","B") 

# A basic Data Class
 
# Importing dataclass module
''' from dataclasses import dataclass,asdict
import pandas as pd

@dataclass
class trade_real_time_data():
	"""A class for holding an article content"""

	# Attributes Declaration
	# using Type Hints

	order_id: str
	strategy_id: str
	is_hedged: bool
	is_squaredoff:bool
	original_traded_price:float
	realtime_price:float
	squaredoff_price:float
	sl_price: float
	tp_price:float
	sl_hit:bool
	tp_hit:bool
	order_type:str
df = pd.DataFrame
# A DataClass object
arti = trade_real_time_data("56ufuf","str5_55",True, False,100.0,125.0,125.0,125.0,150.0,True,False,"BUY")
articles = [arti] 
arti5 = trade_real_time_data("66ufuf","str6_66",True, False,500.0,625.0,625.0,725.0,850.0,True,False,"SELL")
articles.append(arti5)
print(type(asdict(arti5)))
print(type(articles)) 

df = pd.DataFrame([vars(p) for p in articles])
#df.add(arti5)

print(df) '''


