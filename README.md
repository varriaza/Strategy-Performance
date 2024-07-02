# Strategy-Performance
## Link to results write-up
[Everyone Asks Why DCA but Nobody Asks How to DCA? - An analysis of how to DCA best](https://github.com/varriaza/Strategy-Performance/wiki/Everyone-Asks-%22Why-DCA%22-but-Nobody-Asks-%22How-to-DCA%3F%22-%E2%80%90-An-analysis-of-how-to-DCA-best)
  
## What is this project about?
I am looking to compare how different trading strategies for ETH-USD have behaved over different time periods, with a focus on dollar cost averaging. 

## My reason for making this
Dollar Cost Averaging (DCA) is widely regarded as the golden standard for regular people looking to start investing in the stock market. It provides hedges against downward price fluctuations while being very easy to understand. This volatility buffer seemed perfect for crypto and made me wonder, "does it make a difference to DCA once an 1 hour vs once a month"? Given the high volatility in crypto I figured the shorter time between DCA buys would give better returns. This project is designed to test that hypothesis and satisfy my curiosity.

## Code summary:
- Data is collected from kaggle, CoinBase, Binance and etc.
    - Created in '.init_data.ipynb'
- Datasets for price_periods are created (ETH-USD price over a given time period, basically a subset of historical data)
    - These price_periods are meant to be examples of high level market activity
        - The price_period 'low to high to low' captures the price going from a low value to a high value and then back to a low value
    - Created in './init_data.ipynb'
- Each strategy inherits from base_strategy and has a 'run_logic' function
    - Strategies can take inputs to allow for variations, such as, DCA every 1, 7, 14, 30 days.
    - Strategies call shared functions from the base strategy class like buy/sell, move forward in time and create results
    - The function 'run_logic' has the code that makes a strategy work
        - Aka for DCA it would check if x amount of time has passed, then buys a preset amount
- Run strategies for price periods you want
    - See './create_tables.ipynb'
    - This saves the results to 'results/Overall_Results.csv'
- Create plots in './create_plots.ipynb'
- Analyze and write up summary of the data/plots in TBD.txt
- See TODO.txt for what I am currently working on and what I plan to make in the future.

#### ETH price data is taken as the average of price from:
- https://www.kaggle.com/yamqwe/cryptocurrency-extra-data-ethereum
- Binance API
- CoinBase Pro API

#### Price is calculated as: 
- (Open+Close+High+Low)/4
- This will minimize price anomalies or large orders throwing my sources off from the rest of the market.
Price data is taken every minute, which should be a good enough approximation for my purposes.
- This would pose problems if a strategy trades more often than once a minute but I am not planning on creating any like this.

#### Time periods to test (numbers are timestamps):
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

## References and acknowledgments
- HistoricalData.py is taken from: https://github.com/David-Woroniuk/Historic_Crypto/blob/main/HistoricalData.py
    - I did very minor edits, mostly to remove print statements
    - All credit goes to David-Woroniuk
- A big thanks to the following kaggle dataset, CoinBase and Binance for the price data
    - https://www.kaggle.com/yamqwe/cryptocurrency-extra-data-ethereum
- Binance query taken from
    - https://github.com/sammchardy/python-binance
    - pip install python-binance
