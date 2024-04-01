# Prosperity-Trader
This is the repo to test and develop trading algorithm for the IMC prosperity trading challenge.

## Setup
Create a conda environment `trader` and activate the environment with the following command:
```bash
conda create -n trader python=3.12
conda activate trader
```
Install the required packages:
```bash
conda install pandas numpy jsonpickle matplotlib ipykernel
```
Note that `matplotlib` is for visualization, `ipykernel` is required to run the jupyter notebook in the conda environment, neither of them is required for the trading simulation.

## Structure

### Trading strategy
For any given product, calculate its fair market price based on historical data, and make trading decisions based on the difference between the fair market price and the available quotes in the market.
Trading decision may be:
- Buy if the fair market price is higher than the best ask price
- Sell if the fair market price is lower than the best bid price
- Attempt to buy/sell if the fair market price is within the bid-ask spread
The trading decision should also depend on the current position to make sure if the order is matched, it will not exceed the position limit.

The historical data is a time series of the product's price and quantity for each trade and is stored as `traderData`.
Each iteration the trader class `run` method is called, it will analyze the historical data and make trading decisions based on the current market quotes, then update the `traderData`.

### Model for calculating fair market price with historical data


### Code to load and preprocess log data returned from the simulator
This is to prepare the data for analyzing market dynamics and developing 