# Strategy-Performance
Compare how different trading strategies for ETH-USD have behaved over different time periods.

ETH Price Data is taken from:
https://www.kaggle.com/yamqwe/cryptocurrency-extra-data-ethereum

I did not include the data in this repo as it would take decent amount of space and this is very much WIP.
Price is currently calculated as: (Open+Close+High+Low)/4
Since the data is captured once a minute, that should be a good enough approximation for my purposes.
This could pose problems if a strategy trades more often than once a minute.

Time periods to test:
- 3 Years	
- 2 Years	
- 1 Year	
- High to low	
- Low to high	
- High to high	
- Low to low	
- High to medium	
- Med to high
- Low to high to low

Strategies to test:
- DCA every 1 month									
- DCA every 14 days									
- DCA every 7 days									
- DCA every 1 day
- DCA every 1 hour									
- Moving Avg as indicators for buy and sell (buy and sell)									
- Log fit (similar to DCA but only buy when price is below log fit) buy every 1 month
- Log fit buy every 14 days									
- Log fit buy every 7 days
- Log fit buy every 1 day	
- Log fit buy every 1 hour								
- Log fit buy (when below) and sell (when above) every 1 month									
- Log fit buy and sell every 14 days									
- Log fit buy and sell every 7 days	
- Log fit buy and sell every 1 day
- Log fit buy and sell every 1 hour
- Buy and sell based on fear and greed index
- Combo of fear/greed and log fit
- DCA buy over night and DCA sell during the day
- DCA buy over weekends, DCA sell during the weekday
- DCA buy at weekend nights and DCA sell during weekday days 
- Simple momentum buy and sell							
- Neural Network									
- Other ML?

Extra Info per Strategy per time period:
- Time period price delta (start to end)
- Time period % price delta
- Starting USD
- Starting ETH
- Ending ETH # different than returns in ETH as that is total value
- Total returns in USD (aka ending ETH+USD)
- Total returns in # ETH (aka ending ETH+USD in ETH value)
- % Total Returns (in USD) 
- Total trades made
- Flat Return Per Trade # Average dollar amount made per trade
- % return per trade (Helps show how intensive a strategy might be, also can be used for fees)
- Volatility of price for time period (Sharpe Ratio)
- Negative volatility of price (Sortino Ratio)
- Volatility of returns (Sharpe Ratio)

How do I display this?
- Break each table into specific time periods (I think this is best)
    - So the Low to low table would have the "Extra Info" as columns and strategies as rows
        - This way we can compare the strategies in the same time periods
    - I will also make a table for the strategies overall
        - aka the "DCA every 1 day" table would have the "Extra Info" as columns and time periods as rows

Overall logic Summary:
- Break price/time data into time periods
- Make each strategy a class and give them a "run simulation" function
    - Run simulation has the logic that makes the function actually run
    - Call each of those functions from a central location (jupyter notebook for nice formatting?) 
- For each strategy, run on each time period
    - Strategies are their own python script 
        - Make them classes that inherent from a base strategy class
        - Base strategy class has (WIP)
            - Strategy Name
            - Has current amount of USD
            - Current amount of ETH
            - Current date
            - Current price
            - \# trades made
            - Start time # set by strat, referenced by stepping func 
            - End time # set by strat, referenced by stepping func
            - A dataframe of returns over time (used for final data analysis)
                - \# of ETH
                - \# of USD
                - Total value in USD
                - % return from starting USD
            - Price/Time stepping function
            - Sell function, takes in (amount) and uses current price
            - Buy function, takes in (amount) and uses current price
    - They call a shared price/time movement function
        - Strategy has current time and next time it wants to get price
        - Loop until current time > next time (but update the returns over time df) 
        - Perform logic, loop more 
- Save results to a time period results table inside a csv file   
    - If time period file exists, check if strategy is already a row. If it is, replace it, if not append new data.

Summary (to be implemented):
- Create csv files for all time frames
- Create csv with all values for logic that needs to run at the beginning of a strategy for setup (only give the strategy access to data it would have had at the start.)
- Create strategy in its own python file, make it inherit from base strategy class.
- Call strategy in Overall jupyter notebook for ease of running and possible loops (see create_tables.ipynb)
    - Cell creates instance of the specific strategy class
        - Sets starting value like money, time period and etc
        - Calls run simulation function
        - Simulation runs through all data in given time period
        - Results are saved to relevant tables

Roadmap:
[ ] - WIP
[x] - Complete

[ ] Make price period name auto read in the price_df of the same name unless a price_df is supplied 
[ ] Create DCA strat
[ ] Test DCA strat on test time period
[ ] Collect data from DCA on real time period
[ ] Create all time periods
[ ] Collect DCA data on all time periods
[ ] Create Log fit buy
[ ] Create Log fit buy and sell 
[ ] Create Buy and sell based on fear and greed index
[ ] Create Combo of fear/greed and log fit
[ ] Create Simple momentum buy and sell							
[ ] Create Neural Network
[ ] Standardize input as 10k
[ ] consider adding exchange cost (.03%? aka 3/100) on every trade
