from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:

    def __init__(self) -> None:
        pass
    
    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        # print("traderData: " + state.traderData)
        # print("Observations: " + str(state.observations))
        position_limit = 20
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            acceptable_price = {"AMETHYSTS": 10000, "STARFRUIT": 4950};  # Participant should calculate this value
            # print("Acceptable price : " + str(acceptable_price))
            # print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
    
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if best_bid > acceptable_price[product]:
                    try:
                        # state.position is only non-empty dict if the product has been traded before
                        if state.position[product] > -position_limit:
                            orders.append(Order(product, best_bid, -(state.position[product]+position_limit)))
                    except KeyError:
                        orders.append(Order(product, best_bid, -1))

            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                if best_ask < acceptable_price[product]:
                    try:
                        # state.position is only non-empty dict if the product has been traded before
                        if state.position[product] < position_limit:
                            orders.append(Order(product, best_ask, position_limit-state.position[product]))
                    except KeyError:
                        orders.append(Order(product, best_ask, 1))

            result[product] = orders
    
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        
        conversions = 1
        return result, conversions, traderData