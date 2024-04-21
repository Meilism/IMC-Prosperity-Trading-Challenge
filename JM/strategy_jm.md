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
The [log_analysis.ipynb](analysis/log_analysis.ipynb) notebook contains my code to extract data from the log files.

The code loads the second and third part of the generated log file ("activity log" and "trade history") into pandas [DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) objects, which can be further analyzed for building predictive models.

### Data Analysis
The [data_analysis.ipynb](analysis/data_analysis.ipynb) notebook contains my code to visualize the historical data and models to calculate the fair market price.

## Market Taking Strategy

If the fair market price is higher than the best ask price, place a buy order with a price equal to the best ask price.
If the fair market price is lower than the best bid price, place a sell order with a price equal to the best bid price.

## Market Making Strategy (non-directional)

Place buy and sell orders simutaneously around the fair market price to make a profit from the bid-ask spread.

To avoid position imbalance to mitigate [intentory risk](https://hummingbot.org/academy-content/what-is-inventory-risk/), the trading decision should also consider the current position.

## Decision making model

Assume in the current iteration $t$, we predict an expected mid price $P(t)$, and we hold a position $h = h_1 + h_2 - h_3$ of the product *at the end of the iteration*. $h_2$ is the number of products we bought from the market, $h_1$ is the number of products we hold from the previous iteration, and $h_3$ is the number of products we sold to the market.

If we predict that the next iteration, the mid price will go from $P(t)$ to $P(t+1)$, without considering the storage cost, then the expected return of holding $h$ position to next iteration is given by:
$$ R_1 = \left(P(t+1) - P(t)\right) \times h $$
This is the profit coming from the predicted price movement.

If there is price fluctuation, say, the quoted ask/bid price from the foreign market is deviated from the expected mid price, then statistically, we can gain from the deviation as well.

More quantitatively, if we see that the total price to import the product from the foreign market $a(t)$ is lower than the expected mid price, then the expected return of buying $h_2$ products at the bid price and selling at the expected mid price to the local market is naively given by:
$$ R_2 = \left(P(t) - a(t)\right) \times h_2 $$

However, the ask-bid spread in the market sometimes is large and do not fluctuate much, which means that we don't have a lot of opportunities to sell the product at the expected mid price at current moment.
Then we can just assume that we can sell it at some offset from the mid price, say the offset is $s_1\sim 3.5$, the expected sell price of the $h_2$ product that we just bought will then be $P(t) - s_1$.
The expected return of buying $h_2$ products at the bid price and selling at the offset price is given by:
$$ R_2 = \left(P(t) - a(t) - s_1\right) \times h_2 $$

Similarly, if we see a bid price $b(t)$ in the market, we can sell the product at the bid price and buy it back later. 
Then the expected return of selling $h_3$ products at the bid price and buying back at the offset price is given by:
$$ R_3 = \left(b(t) - P(t) - s_2\right) \times h_3 $$
where $s_2$ is the offset from mid price that you will be able to buy.

The total expected return of holding $h$ position to the next iteration is given by:
$$ R = \left(P(t+1) - P(t)\right) \cdot (h_1 + h_2 - h_3) + \left(P(t) - a(t) - s_1\right) \cdot h_2 + \left(b(t) - P(t) - s_2\right) \cdot h_3 $$

Simplied the equation, we have:
$$ R = \left(P(t+1) - P(t)\right) \cdot h_1 +  \left(P(t+1) - a(t) - s_1\right) \cdot h_2 + (b(t) - P(t+1) - s_2)\cdot h_3$$

Include the storage cost, the total expected return of holding $h$ position to the next iteration is given by:
$$ R = \left(P(t+1) - P(t)\right) \cdot h_1 +  \left(P(t+1) - a(t) - s_1\right) \cdot h_2 + (b(t) - P(t+1) - s_2)\cdot h_3 - storage(h_1 + h_2 - h_3) $$

$h_1$ is the position we started with, which we do not have control over. But we can optimize $h_2$ and $h_3$ to maximize the expected return.