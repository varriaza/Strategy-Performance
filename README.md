# Strategy-Performance
Compare how different trading strategies for ETH-USD have behaved over different time periods.

Time Periods:
- 3 Years	
- 2 Years	
- 1 Year	
- High to low	
- Low to High	
- High to high	
- Low to low	
- High to medium	
- Med to high

Strategies:
- DCA 1m									
- DCA 14d									
- DCA 7d									
- DCA 1d									
- Moving Avg b/s									
- Log fit buy 1m									
- Log fit buy 14d									
- Log fit buy 7d									
- Log fit b/s 1m									
- Log fit b/s 14d									
- Log fit b/s 7d									
- Neural Network									
- Other ML?

Why log fit?
- ETH is a new project (even still) and will have exponential growth

Extra Info per Strategy per time period:
- Price delta (start to end)
- % Price delta
- Total Returns in USD (aka ETH+USD)
- Returns in # ETH
- % Total Returns (in USD) 
- Total trades made
- % return per trade (Helps show how intensive a strategy might be, also can be used for fees)
- Volatility of price (Sharpe Ratio)
- Negative volatility of price (Sortino Ratio)
- Volatility of returns (Sharpe Ratio)
- Other return metrics?
How do I display this? It breaks the table style logic with strategies as rows and time periods as columns.
- Maybe a table within a table?
- Maybe break each table into specific time periods (I think this is best)

Overall logic Summary:
- Break price/time data into time periods
- Make each strategy a class and give them a "run simulation" function
    - Run simulation has the logic that makes the function actually run
    - Call each of those functions from a central location (jupyter notebook for nice formatting?) 
- For each strategy, run on each time period
    - Strategies are their own python script 
        - Make them classes that inherent from a base strategy class
        - Base strategy class has
            - Strategy Name
            - Has current amount of USD
            - Current amount of ETH
            - Current date
            - Current price
            - \# trades made
            - A dataframe of returns over time
                - \# of ETH
                - \# of USD
                - Total value in USD
                - % gain from starting USD
            - Price/Time stepping function
            - Sell function, takes in (amount) and uses current price
            - Buy function, takes in (amount) and uses current price
    - They call a shared price/time movement function
        - Strategy has current time and next time it wants to get price
        - Loop until current time > next time (but update the returns over time df) 
        - Perform logic, loop more 
- Save results to a (central or individual?) results file   
    - If saved to individual file merge into main file at the end for a nice summary

Summary:
- Define all time frames in a cell
- Run strategy cell in Overall jupyter notebook
- Cell creates instance of strategy class
- Sets starting value like money
- Calls run simulation function for each time frame
- The sim 
