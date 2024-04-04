## Structure

### Trading strategy
For any given product, calculate its fair market price based on historical data, and make trading decisions based on the fair market price and the outstanding orders in the market.

Trading decision may be:
- Buy if the fair market price is higher than the best ask price
- Sell if the fair market price is lower than the best bid price
- Attempt to buy/sell if the fair market price is within the bid-ask spread

The trading decision should also depend on the current position to make sure if the order is matched, it will not exceed the position limit.
And to avoid position imbalance to mitigate [intentory risk](https://hummingbot.org/academy-content/what-is-inventory-risk/), the trading decision should also consider the current position.

### Model for calculating the fair market price
The input should be 

### Decision making based on the model outputs

**Market Making Strategy**


**Trend Following Strategy**