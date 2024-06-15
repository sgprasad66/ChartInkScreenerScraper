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

For placing F and O segment trades run "Finvasia_Get_Strike_From_Given_Premium.py" to place orders before market opens.

I have listed a backlog of tasks planned for the coming days, includes enhancements and refactoring/restruccturing of existing code.Any one interested
in contributing in this effort please feel free change the code ,code new strategies for example- calendar spreads,diagonal calendar spreads,covered calls,
commodity trades or even forex trades. I would love to collaborate with anyone offering coding support or by way of domain knowledge support to enhance 
the strategies,do get in touch with me.

1.F&O stocks if they are in the ban list-How to handle the situation.

2. Whenever the connection to internet is disrupted how to regenerate the websocket token connections that were already established when the trading had happened earlier.

3.Whenever we go for deep ITM call/put options,if the strike has no or low volume should we change the chosen strikes.

4.Include token-for index and stock calls/puts -in the Mongo database.

5.Include logic for trailing stop-loss and target. When any one leg hits SL or TP, take care of SLs and TPs for the other associated legs for that trade.

6.Include logic for trading in calendar spreads-at the start of the months- both for NIFTY and BANKNIFTY.

7.Handle the case for including Short Straddle according to the day of the week. Mon - MidcapIndex, Tue - FINNIFTY, Wed - BANKNIFTY, Thurs - Nifty. Preferably these should be traded @.10.00am and Exited by 2.00pm or max 3pm.

8.Code for Ratio spreads( 1 ATM Buy and 2 OTM Sell both for Call/Put with matching premia so we stay fully hedged.),Delta-neutral strategy for BANKNIFTY,strategies for super bullish/bearish scenarios.

9.Include option for manual intervention. Supposing a two-legged strategy is performing poorly,neither hitting SL or TP, have a mechanism thro UI to show the trades and option to exit a single leg or liquidate the complete trade.Here we also need to have an option where the user can say liquidate all trades for the day and not take any further trades for the day.

10.Logging using default logger,remove all print statements.

11.Refactor the code so that it supports Dependency Injection,Repository Pattern-protect against underlying database changes, put the secrets,keys,username.pwds etc in the environment and retrieve it from there and other industry best practices???Based on bandwidth and availability of personnel??Low priority.

12.Include buzzing stocks, toast of the season shares in the analysis pipeline and take appropriate actions.Basically listen to the social media viral news and include in your analysis both on the up and down side.

13.Pick up the analyst recommendations live from TV and evaluate with our criteria and place matching trades appropriately.Explore Speech-to-text transcoding li braries in the market and translation from hindi to English services. Utilize Named-Entity-Recognition,NER for identifying the stocks from the generated text and analyse the sentiment and extract the trading recommendation and act accordingly.

14.Intoduce ML and RL based algorithms in the processing pipeline mix.Employ the PPO - with RLHF algo - the current buzz in the market.

15.Intruduce a scoring mechanism - similar to CIBIL score - taking into account all the features concerned and assign appropriate weights before arriving at a score for the individual stocks and based on the score arrived at take a trade -either buy/sell/no-trade. Something on the lines of CIBIL. Remember,If the CIBIL is below 750,no loans offered by the private/public sector banks.

16.Debate on a good Interprocess mechanism,like PIPES,Multiprocessing Queues,SOCKETS for real time communication between two python programs or scripts.Identify the best 
practice for our scenario.

17.Explore options to convert the python scripts/programs to serverless functions/AWS Lambdas/GCP-based mechanisms to put them on the cloud freeing our personal laptops. 

18.Provide a common UI interface integrating all the scripts,configurations,dependencies etc so the user does not have to run scripts separately and remember all the configuration changes to be carried out each day at the start of the trading session.-Partially done?

19.How to package together all the scripts,packages,programs for easy or one-click deployment. Explore Docker for the same.Kubernetes??

20.Have all the scripts write to a common log file that could be used for run-time diagnostics to identify issues occuring while running the programs.

21.Use relative paths for all file related operation.Remove all hard-coded paths and use relative path.

22.Provide support for other broker APIs like Zerodha,Alice Blue, Fyers etc.

23.Move some common funtionality to a single file like Utilities or Utilities folder and group the common files there. Come up with a logical-functional folder structure and segragate the files into them as appropriate.Partially done?


