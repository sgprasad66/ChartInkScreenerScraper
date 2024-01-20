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

Particularly supports a strategy where we place  calls/puts and sell  one call/put which is roughly equal to the bought calls/puts.

For example:
If the Nifty (or Banknifty or any other stock) is at say 21,622 we consider the ATM as 21600. 
Leg-1: Buy 2 quantities of 21600 CALL trading at say 250 premium.
Leg-2: Sell 1 quantity of say 21300 CALL trading at say 512 premium.

The thought process is like so: Since we are buying ATM Calls if the index/stock goes up significantly the ATM calls will gain value faster than the deep ITM CALL
which we have sold. So the 21600 CALLs would say double while the 21300 CALL would have say moved up by 60-70% only. This difference in premia is what we try to cash
and exit our positions programmatically. Say when this difference is two thousand rupees in our favour exit both the legs.
Same holds true for a bearish market.Buy 2 ITM PUTS and sell one deep ITM PUT.Again the mechanism comes into play and when our fixed target is reached exit both the legs.
But remember to exit on the Loss side also.
This seems to work very well for individual stocks. Like yesterday OFSS stock went up by 7-8% intraday. The above strategy ended up with Rs.22000 -Rs.25000 difference.
Automatically exiting the positions has not been implemented yet, will check-in shortly.

This should gell well with the chartink screen scraper.The screen scraper generates four bins - positional/medium term bullish,intraday bullish,positional/medium term bearish
and intraday bearish. Use those bins generated automatically to create the above startegy and automate the exits accordingly. This should give you significant profits.
Please try out the above startegy and let me know the results.
