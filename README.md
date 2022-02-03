# Strategy-Performance
What is this project about?
I am looking to compare how different trading strategies for ETH-USD have behaved over different time periods, with a focus on dollar cost averaging. 

Why make this?
Dollar Cost Averaging (DCA) is widely regarded as the golden standard for regular people looking to start investing in stock.
It provides hedges against losing value from price fluctuations and market crashes while being very easy to understand. This makes DCA a great fit for cryptocurrencies due to their high volatility. However, due to the complexities of time activated smart contracts, gas and MEV, automated DCA apps have been notably absent from DeFi. Using the results from this project I am hoping to add more focus on why and how badly DCA DeFi apps are needed. If DeFi hopes to become an accepted and standardized way for regular people to have more control over their savings/investments, they need more tools to empower them to make smart actions. I see a need for these apps and few advocating for the attention I feel this problem deserves.

Why ETH?
Ethereum is how I got into the wonderful world of cryptocurrency and DeFi so it only felt natural to use it. However, I have constructed the code to make it very easy to collect data on other pairs. Simply change the API calls to the desired pair then call the strategies with the pair data. In the future I plan to update the code to accept coin names so that the results will automatically update for your desired pair.

What will happen when data collection is finished?
I will be writing up two summary posts. Both will be uploaded freely to the internet via Reddit, medium or other methods.
    1) Why we need DCA DeFi apps, aka how much benefit does DCA bring to cryptocurrency investing? Are certain kinds of DCA strategies better than others?
    2) How do a bunch of strategies compare during different price periods? This is more for the advanced trader rather than investors.

How do I run this?
- Collect data from kaggle, CoinBase and/or Binance
    - Created in ini_data.ipynb
- Create price period data
    - Make sure your data has prices for all of the price periods you will be creating
    - Created in ini_data.ipynb
- Run strategies for price periods you want
    - Run create_tables.ipynb with your data

ETH Price Data is taken as the average of price from:
- https://www.kaggle.com/yamqwe/cryptocurrency-extra-data-ethereum
- Binance API (WIP)
- CoinBase Pro API (WIP)

Data Notes:
- I did not include the source price data in this repo as it would take a decent amount of space and is very much WIP.
    - I will provide a script that:
        - can be run to re-create the Binance and CoinBase data.
        - will format the kaggle data into the format I used.
    - Anyone will be able to recreate the results I found, add new strategies or look at new crypto pairs.
- Price is currently calculated as: (Open+Close+High+Low)/4. I then take the average from the three sources I have.
    - This will minimize price anomalies or large orders throwing my sources off from the rest of the market.
- Price data is taken every minute, which should be a good enough approximation for my purposes.
    - This would pose problems if a strategy trades more often than once a minute but I am not planning on creating any like this.

Time periods to test (numbers are timestamps):
- Past 4 Years
    - 2018 through 2021
- Past 3 Years 
    - 2019 through 2021
- Past 2 Years 
    - 2020 through 2021
- Past 1 Year 
    - all of 2021 # Low to high to low to high
- High to low 
    - 1515870180 (max of 2018) to end of 2018
    - 1620125000 (before 2021 crash) to 1627000000 (2021 crash low)
- Low to high 
    - start of 2020 to 1620125000 (before 2021 crash)
    - 1627000000 (2021 crash low) to end of 2021
- Low to high to low
    - all of 2019
    - 2021 start to 1627000000 (2021 crash low)
- High to low to high
    - 1515870180 (2018) to 1620125000 (before 2021 crash)
    - 1620125000 (before 2021 crash) to end of 2021

Strategies to test:
- 100% all in right away
- FOMO in only (invest if asset has gone up x% in past y days), don't sell
- FOMO in and out, FOMO buy and then sell after x% drop in past y days
- DCA every 1, 7, 14, 30 days									
- DCA every 1 hour									
- Moving Avg as indicators for buy and sell
- Log of Moving Avg as indicator for buy and sell						
- Log fit (similar to DCA but only buy when price is below log fit) buy every 1, 7, 14, 30 days							
- Log fit buy every 1 hour								
- Log fit buy (when below) and sell (when above) every 1, 7, 14, 30 days
- Log fit buy and sell every 1 hour
- Buy and sell based on fear and greed index
- Combo of fear/greed and log fit
- DCA buy over night and DCA sell during the day
- DCA buy over weekends, DCA sell during the weekday
- DCA buy at weekend nights and DCA sell during weekday days 
- Simple momentum buy and sell							
- Neural Network									
- Other ML?

Results captured per Strategy per time period:
- Time period price delta (start to end)
- Time period % price delta
- Starting USD
- Starting ETH
- Ending USD
- Ending ETH # different than returns in ETH as that is total value
- Total value in USD (total ending value for ETH+USD in USD)
- Total returns in USD (aka ending ETH+USD in USD minus starting ETH+USD)
- Mean of the Annualized % Return over time
- Median of the Annualized % Return over time
- Final Annualized % Return
- Median-Mean of the Annualized % Return (Useful to see how big the outlier returns were)
- Total number of trades made (Helps show how intensive a strategy might be, also can be used for gas fee estimation later)
- Total of fees paid (.3% is taken off of ever trade to model the Uniswap costs)
- Flat Return Per Trade (Average dollar amount made per trade)
- % return per trade
- Volatility of returns (Sharpe Ratio)
- Negative volatility of price (Sortino Ratio)
- Standard deviation of price (Measures volatility of price)

How do I save the results?
- Similar price_period and strategy results are saved together to allow for easy comparison between:
    - different strategies in the same price period
    - different price periods for the same strategy

Overall logic Summary:
- Break price/time data into time periods
- Make each strategy a class and give them a "run_logic" function
    - run_logic has the code that makes a strategy work
        - Aka for DCA it would check if x amount of time has passed, then buys a preset amount
    - Call each of those functions from a central location (jupyter notebook for nice formatting) 
- For each strategy, run on each time period
    - Strategies are classes that inherent from a base strategy class
        - This allows for multiple variations of strategies, for example, DCA every 1, 7, 14, 30 days.
    - They call shared functions from the base strategy class like buy/sell, move forward in time and create results
        - Strategy has current time and next time it wants to get price
        - Loop until current time > next time (but we keep track of the returns over time) 
        - Perform logic, loop more 
- Save results to a time period results table inside a csv file   
    - If time period file exists, check if the strategy already has a row. If it does, replace it, if not append new data.
