Assume in the current iteration $t$, we predict an expected mid price $P(t)$, and we hold a position $h = h_1 + h_2 - h_3$ of the product *at the end of the iteration*. $h_2$ is the number of products we bought from the foreign market, $h_1$ is the number of products we hold from the previous iteration, and $h_3$ is the number of products we sold to the local market.

If we predict that the next iteration, the mid price will go from $P(t)$ to $P(t+1)$, without considering the storage cost, then the expected return of holding $h$ position to next iteration is given by:
$$ R_1 = \left(P(t+1) - P(t)\right) \times h $$
This is the profit coming from the predicted price movement.

If there is price fluctuation, say, the quoted ask/bid price from the foreign market is deviated from the expected mid price, then statistically, we can gain from the deviation as well.

More quantitatively, if we see that the total price to import the product from the foreign market $a(t)$ is lower than the expected mid price, then the expected return of buying $h_2$ products at the bid price and selling at the expected mid price to the local market is naively given by:
$$ R_2 = \left(P(t) - a(t)\right) \times h_2 $$

However, the ask-bid spread in the local market is large and do not fluctuate much, which means that we don't have a lot of opportunities to sell the product at the expected mid price.
Since the ask-bid spread is stable, we can just assume that we can sell it at some offset from the mid price, say the offset is $s_1\sim 3.5$, the expected sell price of the $h_2$ product that we just bought will then be $P(t) - s_1$.
The expected return of buying $h_2$ products at the bid price and selling at the offset price is given by:
$$ R_2 = \left(P(t) - a(t) - s_1\right) \times h_2 $$

Similarly, if we see a bid price $b(t)$ in the local market, we can sell the product at the bid price and buy it back from the foreign market. To buy from the foreign market, on average we need to pay the ask price + the import tariff + transport fee, so the buy price will be $P(t) + s_2$, where $ s_2  $ should include the foreign market ask to mid price spread, the import tariff, and the transport fee.
Then the expected return of selling $h_3$ products at the bid price and buying back at the offset price is given by:
$$ R_3 = \left(b(t) - P(t) - s_2\right) \times h_3 $$
where $s_2 \sim 0.75 + import\_tariff + transport\_fee$.

The total expected return of holding $h$ position to the next iteration is given by:
$$ R = \left(P(t+1) - P(t)\right) \cdot (h_1 + h_2 - h_3) + \left(P(t) - a(t) - s_1\right) \cdot h_2 + \left(b(t) - P(t) - s_2\right) \cdot h_3 $$

Simplied the equation, we have:
$$ R = \left(P(t+1) - P(t)\right) \cdot h_1 +  \left(P(t+1) - a(t) - s_1\right) \cdot h_2 + (b(t) - P(t+1) - s_2)\cdot h_3$$

Include the storage cost, the total expected return of holding $h$ position to the next iteration is given by:
$$ R = \left(P(t+1) - P(t)\right) \cdot h_1 +  \left(P(t+1) - a(t) - s_1\right) \cdot h_2 + (b(t) - P(t+1) - s_2)\cdot h_3 - storage(h_1 + h_2 - h_3) $$

$h_1$ is the position we started with, which we do not have control over. But we can optimize $h_2$ and $h_3$ to maximize the expected return.