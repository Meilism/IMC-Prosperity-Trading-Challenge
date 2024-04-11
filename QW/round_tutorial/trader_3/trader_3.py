from datamodel import OrderDepth, UserId, TradingState, Order, Trade
from typing import List
import numpy as np

class Trader:

    def __init__(self) -> None:
        self.market_mid_prices = {}

    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        # print("traderData: " + state.traderData)
        # print("Observations: " + str(state.observations))
        position_limit = 20
        samp_size = 40
        result = {}
        for product, order_depth in state.order_depths.items():
            orders: List[Order] = []

            if len(order_depth.buy_orders) == 0 or len(order_depth.sell_orders) == 0:
                continue

            bid_prices = list(order_depth.buy_orders.keys())
            bid_quantities = list(order_depth.buy_orders.values())
            bid_ave_price = np.average(bid_prices, weights=bid_quantities)

            ask_prices = list(order_depth.sell_orders.keys())
            ask_quantities = list(order_depth.sell_orders.values())
            ask_ave_price = np.average(ask_prices, weights=ask_quantities)

            mid_price = (bid_ave_price + ask_ave_price) / 2
            try:
                self.market_mid_prices[product].append(mid_price)
                self.market_mid_prices[product] = self.market_mid_prices[product][-samp_size:] # only keep the last samp_size elements to avoid memory overflow
            except KeyError:
                self.market_mid_prices[product] = [mid_price]
                continue

            if len(self.market_mid_prices[product]) < samp_size:
                continue

            popt = np.polyfit(np.arange(samp_size), self.market_mid_prices[product], 2) # fit to a quadratic function, popt in reducing order of power
            a = popt[0] # coefficient of x^2
            b = popt[1] # coefficient of x
            c = popt[2] # constant term
            x = samp_size # correspond to next time stamp
            acceptable_price = a*x**2 + b*x + c # projected price at next time stamp

            try:
                # state.position is only non-empty dict if the product has been traded before
                pos = state.position[product]
                for ask_price, ask_amount in order_depth.sell_orders.items():
                    if ask_price < acceptable_price and pos < position_limit:
                        q = min(-ask_amount, position_limit - pos)
                        orders.append(Order(product, ask_price, q))
                        pos += q
                    else:
                        break
            except KeyError:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                if best_ask < acceptable_price:
                    orders.append(Order(product, best_ask, 1))

            try:
                # state.position is only non-empty dict if the product has been traded before
                pos = state.position[product]
                for bid_price, bid_amount in order_depth.buy_orders.items():
                    if bid_price > acceptable_price and pos > -position_limit:
                        q = min(bid_amount, pos + position_limit)
                        orders.append(Order(product, bid_price, -q))
                        pos -= q
                    else:
                        break
            except KeyError:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if best_bid > acceptable_price:
                    orders.append(Order(product, best_bid, -1))

            result[product] = orders
    
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        
        conversions = 1
        return result, conversions, traderData