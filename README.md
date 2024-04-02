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
For any given product, calculate its fair market price based on historical data, and make trading decisions based on the fair market price and the outstanding orders in the market.

Trading decision may be:
- Buy if the fair market price is higher than the best ask price
- Sell if the fair market price is lower than the best bid price
- Attempt to buy/sell if the fair market price is within the bid-ask spread

The trading decision should also depend on the current position to make sure if the order is matched, it will not exceed the position limit.
And to avoid position imbalance in the case of unwanted market movement, the trading decision should also consider the current position.

All user data is stored in `traderData` and needs to be serialized to `string` object before returning to the simulator.
```python
import jsonpickle
traderData = jsonpickle.encode(traderData)
```
To use the `traderData` in the next iteration, deserialize the `string` object back to `traderData`.
```python
traderData = jsonpickle.decode(traderData)
```

### Structure of `traderData`
The `traderData` serves as a container for all the necessary data for the trading decision.
It is a dictionary keyed by the product name, and the value is another dictionary-like object `ProductData` with the following properties:
- `position`: the current position of the product
- `position_limit`: the maximum position allowed for the product
- `previous_fair_price`: the fair market price calculated from the previous iteration
- other quantities that are necessary for the pricing model

### Model for calculating the fair market price
The input should be 

### Code to load and preprocess log data returned from the simulator
This is to prepare the data for analyzing market dynamics and developing effective trading strategies.