# Prosperity-Trader
This is the repo to test and develop trading algorithm for the IMC prosperity trading challenge.
Our team is `Quantum_Quintet` and we ended up in the 120th among 10,020 competing teams after the final round.
The ranking can be found [here](https://jmerle.github.io/imc-prosperity-2-leaderboard/).

**Round 1**

This round there are two products to trade: AMETHYSTS and STARFRUIT. 
AMETHYSTS has stable prices while STARFRUIT price drift over time. 
We simply market-take and market-make around the expecced prices.
Since the products are very similar to last year and are also the same to the tutorial round, this round's leaderboard is very competitive.
The manual challenge is quite simple, and a lot of teams got similar scores.
We ended up in 431st place.

**Round 2**

This round a new product is introduced: ORCHIDS.
This product can be traded in both local market similar to AMETHYSTS and STARFRUIT and a foreign market via conversion requests.

We use an arbitraging strategy to sell ORCHIDS in the local market and convert the position through the foreign market.
Because this product is more complicated, we sort of rushed the implementation and did not have enough time to test the strategy.
We actually made a mistake in our understanding of the conversion request and missed ~50% of the profit, and did not use a dynamic pricing approach which could in principle help to gain more when the price difference between two markets is more favorable.

The manual challenge is also quite simple for this round.
We ended up in 275th place after the round.

**Round 3**

This round 4 products are introduced: GIFT_BASKET, STRAWBERRIES, CHOCOLATE, and ROSES.
GIFT_BASKET is a bundle of STRAWBERRIES, CHOCOLATE, and ROSES.

We use a threshold-based strategy to trade the GIFT_BASKET and use the individual products to hedge the position.
We also discovered our mistakes in the previous round and implemented a dynamic pricing approach to maximize the profit.
However, the profit from ORCHIDS is cut down in this round (and all the following rounds) because of the high import tax.

The manual challenge involves some estimation on other teams' strategies.
We ended up in 239rd place after the round.

**Round 4**

This round 2 new products are introduced: COCONUT and COCONUT_COUPON. The coupon is a product similar to an American call option on COCONUT.
We ended up studying the black-scholes model to price the COCONUT_COUPON and trade around it, while using the COCONUT to hedge the position.

The manual challenge is quite similar to the first round's manual challenge, with some modifications on the return if your bid is lower than average bid from all participanting teams.
We choose to bid a little bit higher than our bid in the first round.

We ended up in 166th place after the round.

**Round 5**

This round there is no new product introduced.
However, the information about the counterparties is provided.

While studying the bots behaviors, we found that some of them (V's bots) are market makers who send orders on both sides of the order book.
The other trader bots trade less frequently.
However, we did not think of a way to take advantage of this information and ended up with the same algorithm as the previous round.

For the manual challenge, we were given a news paper and need to estimate the impact of the news on the market to decide on the trading strategy.
Our estimation is moderately accurate and gained about 120k, while the optimal strategy could gain about 150k.

We ended up in 120th place after the round.

## Setup
Create a conda environment `trader` and activate the environment with the following command:
```bash
conda create -n trader python=3.12
conda activate trader
```
Install the required packages:
```bash
conda install pandas numpy jsonpickle matplotlib ipykernel statsmodels
```
Note that `matplotlib` is for visualization, `ipykernel` is required to run the jupyter notebook in the conda environment, neither of them is required for the trading simulation.

**Example**
An example [trader.py](trader.py) is provided in the repo.
The file is an empty skeleton and does not have any trading strategy coded up.

:warning: **People could make their own copy of the file as `trader_<name>.py` and implement their own trading strategy.**

## Use the Visualizer and Back-tester
The skeleton file contains the necessary modification to use the [IMC Prosperity 2 Visualizer](https://jmerle.github.io/imc-prosperity-2-visualizer/).

**Visualizer**
To use the visualizer, follow the steps below:
1. Modify the `trader_<name>.py` file to implement your own trading strategy.
2. Upload the `trader_<name>.py` to the Prosperity server.
3. After the server finishes the simulation, download the log file from the server and upload it to the visualizer.
4. Check out the performance of your trading strategy there!

**Back-tester**
To use the [backtester](https://github.com/jmerle/imc-prosperity-2-backtester), follow the online instructions to install the package and run in the terminal.
Note that the code only does the order matching on the existing orders in `order_depth`, but in the real prosperity server, the order matching can also happen with hidden orders with virtual bots.

The backtester package is compiled to load data from some `.csv` files stored under `[installation folder for the package]/resources/` which are extracted from prosperity log files.
Since it also provides support for custom data source, I also create a `shared_data` folder to store some custom data files.

To use the backtester, follow the steps below:
1. Modify the `trader_<name>.py` file to implement your own trading strategy.
2. Install the backtester package
3. Run the backtester with the following command to get the results for a specific round:
```bash
prosperity2bt <path-to-your-file> <round-number> --data shared_data
```
Note that by specifying the `--data shared_data` flag, the backtester will load the data from the `shared_data` folder.

## Use `traderData` to store data between iterations
The algorithm needs some data to make trading decisions, which should be stored in the `traderData` object to make sure it is persistent between iterations.

All user data is stored in `traderData` and needs to be serialized to `string` object before returning to the simulator.
```python
import jsonpickle
traderData = jsonpickle.encode(traderData)
```
To use the `traderData` in the next iteration, deserialize the `string` object back to `traderData`.
```python
traderData = jsonpickle.decode(traderData)
```

## Submissions
Our algorithm submissions are stored under the `submissions` folder along with the result log.