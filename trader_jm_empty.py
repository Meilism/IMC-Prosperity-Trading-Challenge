from datamodel import Listing, Trade, OrderDepth, UserId, TradingState, Order
from typing import List

class Trader:
    
    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        
        result = {}
        for product in state.order_depths:
            orders: List[Order] = []            
            result[product] = orders
    
        traderData = "" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        conversions = 0
        return result, conversions, traderData