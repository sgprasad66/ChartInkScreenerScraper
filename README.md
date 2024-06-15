# ChartInkScreenerScraper

This set of python scripts can be used to trade in shares in the indian stock exchanges.

It can place automated orders for stocks in cash and intraday,both buy and sell.

This can also be used to trade using short straddle strategy for banknifty.

Makes use of beautifulsoup to scrape the chartink website to automatically keep running the various screeners on the chartink dashboard and take trades
accordingly with out human intervention.

Would invite pythonistas and market enthusiasts to use this and also improve upon the programs.

Connect with me over mail to discuss and improve this further.

Few screenshots from the scripts developed using PySimpleGUI framework.![intraday_scrips](https://user-images.githubusercontent.com/31882456/232492108-de2f50f4-9256-48de-9761-f97a2a6e9717.png)
![open_positions_UI](https://user-images.githubusercontent.com/31882456/232492123-23bdceca-b9d5-46d3-9c3c-62ea00f91c20.png)

Now using the newly added files create strategies  using Finvasia API which are free unlike Zerodha.

Particularly supports a strategy where we place two buy  calls/puts and sell  one call/put which is roughly equal to the bought calls/puts.

For example:
If the Nifty (or Banknifty or any other stock) is at say 21,622 we consider the ATM as 21600. 

Leg-1: Buy 2 quantities of 21600 CALL trading at say 250 premium.

Leg-2: Sell 1 quantity of deep ITM call,say 21300 CALL trading at say 512 premium.

The main idea is the premium bought should be roughly equivalent to the premium sold.In the above example 250*2=500 which is roughly equivalent to 512.Hence
the loss would not too significant but the profits would be good.

The thought process is like so: Since we are buying ATM Calls if the index/stock goes up significantly the ATM calls will gain value faster than the deep ITM CALL
which we have sold. So the 21600 CALLs would say, double while the 21300 CALL would have say moved up by 60-70% only. This difference in premia is what we try to cash in
and exit our positions programmatically. Say, when this difference is two thousand rupees in our favour exit both the legs.

Same holds true for a bearish market.Buy 2 ITM PUTS and sell one deep ITM PUT.Again the mechanism comes into play and when our fixed target is reached exit both the legs.
But remember to exit on the Loss side also.

This seems to work very well for individual stocks. Like yesterday OFSS stock went up by 7-8% intraday. The above strategy ended up with Rs.22000 -Rs.25000 difference.
Automatically exiting the positions has not been implemented yet, will check-in shortly.

This should gell well with the chartink screen scraper.The screen scraper generates  stocks in four bins - positional/medium term bullish,intraday bullish,positional/medium term bearish and intraday bearish. Use those bins generated automatically to create the above startegy and automate the exits accordingly. This should give you significant profits.

Please try out the above startegy and let me know the results.

Updates:

A new tabbed interface has been checked in,looks like so:

![image](https://github.com/sgprasad66/ChartInkScreenerScraper/assets/31882456/bd67c9ad-ce46-455a-ac34-e449a83e6db3)

To get this screen run "Options_tool_Tabbed_Interface.py" file. We have 4 tabs here:

Global setting - for configuration
Trades/Positions for Nifty/BankNifty/Finnifty/Midcpnifty - for the current positions,mtm,loss,profit,return percentage etc.
Scrip Counts for Intraday - for showing the screeners count for the individual shares.
Processes to Execute - for executing certain processes/scripts -for MySQL table provisioning,pre-market activities and post-markets processing.

There are 4 buttons,these have not been implemented yet. Will be adding/planned to add two more tabs for LLM integration and machine learning incorporation.
Right now for persistence we are using MongoDB, JSON file and MySQL databases. MySQL is working fine but there are issues with MongoDB and JSON file persistence.
Will reimplement them in the coming days.

Alternatively here are the instructions for running the scripts individually-

If only cash stocks follow as given below.

1.Get today's auth code for kite and set it in code or config.
2.You need to create a collection bearing today's  date (eg-15_06_2024) in mongodb .
3. Run the file "ChartInk_Scrape_With_Multiprocess.py" ,this runs the scraping process and starts by creating a folder in your current
executing environment named as the same as given in step-2. It keeps creating csv files containing the scrips which have appeared
in the various screeners at different points of time. Keep this running from 9.15 till 3.30.
4. Run the file "ChartInk_Scaper_FileWatcher_Processor.py". This keeps looking for the new file arrivals in the folder for today i.e. 15_06_2024
created when step-3 runs. As soon as file arrives here we loop through all files and create 4 bins/buckets with names like positional-bullish/intraday-bullish/
positional-bearish/intraday-bearish lists.Here you can tweak the code to your heart's content and implement your own strategy. For example ,start this process
at 11.00am, run this for 1-2 hours and then the strategy could be - get a count of the last 15days of pos-bullish and get the counts of the top-5 say, anything above
250 in the pos-bullish and intraday-bullish should be 10 or above and not appear in the top with a count of 100 in pos-bearish bucket and less than 10 in the intraday-bearish bucket.
Once this criteria is met, place a BUY call for the script appearing in the top of the pos-bullish bucket  and meeting the other criteria specified and similarly a "SELL" for the script that
appears in the pos-bearish bin and not appearing in the bullish bins. This should happen in the code in real-time.
5.Run "Open_Positions_Today_UI.py" to get the screen that will show the current positions/buys/sells,mtm,loss etc.
6.Run "Scrip_Count_Display.py" to show the counts of the scripts appearing in the various bins. You can go back and see for example -from the last 30 days which stock
has appeared in the bullish screeners the most. 
 
The above strategy I have coded and attached to this mail.

If looking for Options the process is different and i will let you know if you want that also.

Let me know if this helps run the code and best of luck.

Let me know if there are any other issues.

