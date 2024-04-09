# Trading Strategy

## Introduction
For any given product, calculate its fair market price based on historical data, and make trading decisions based on the fair market price and the outstanding orders in the market.

Trading decision may be:
- Buy if the fair market price is higher than the best ask price
- Sell if the fair market price is lower than the best bid price
- Attempt to buy/sell with a bid-ask spread around the fair market price

The trading decision should also depend on the current position to make sure if the order is matched, it will not exceed the position limit.

# Notebooks for visualization and analysis
To analyze the historical data and visualize the price dynamics, I have created two Jupyter notebooks:

### Log Analysis
The [log_analysis.ipynb](log_analysis.ipynb) notebook contains my code to extract data from the log files.

The code loads the second and third part of the generated log file ("activity log" and "trade history") into pandas [DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) objects, which can be further analyzed for building predictive models.

### Data Analysis
The [data_analysis.ipynb](data_analysis.ipynb) notebook contains my code to visualize the historical data and models to calculate the fair market price.

## Market Making Strategy (non-directional)

Place buy and sell orders simutaneously around the fair market price to make a profit from the bid-ask spread.

To avoid position imbalance to mitigate [intentory risk](https://hummingbot.org/academy-content/what-is-inventory-risk/), the trading decision should also consider the current position.


## Trend Following Strategy (directional)