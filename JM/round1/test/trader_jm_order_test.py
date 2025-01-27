import json, jsonpickle
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any, List, Dict
from collections import defaultdict

ORDER = False

TRADER_DATA = {
    'AMETHYSTS': {        
        'price_method': 'static',

        'mid_price': 10000,
        'buy_price': 9998,
        'sell_price': 10002,

        # 'mid_price': None,
        # 'buy_price': None,
        # 'sell_price': None,

        'position_limit': 20,
        'position_stage_1': 0,
        'position_stage_2': 20,
        
        'excess_buy': [(9995, 0.1), (9996, 0.1), (9998, 0.8)],
        'excess_sell': [(10005, 0.1), (10004, 0.1), (10002, 0.8)],

        # 'excess_buy': None,
        # 'excess_sell': None,
    },
    'STARFRUIT': {
        'price_method': 'average',
        'price_data_size': 8,
        'price_data': [],
        'price_spread': [-2, 2],

        # 'price_method': 'weighted_average',
        # 'price_data_size': 8,
        # 'price_data': [],
        # 'price_spread': [-2, 2],

        'mid_price': None,
        'buy_price': None,
        'sell_price': None,

        'position_limit': 20,
        'position_stage_1': 0,
        'position_stage_2': 20,
        
        'excess_buy': None,
        'excess_sell': None,
    },
}

class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        print(json.dumps([
            self.compress_state(state),
            self.compress_orders(orders),
            conversions,
            trader_data,
            self.logs,
        ], cls=ProsperityEncoder, separators=(",", ":")))

        self.logs = ""

    def compress_state(self, state: TradingState) -> list[Any]:
        return [
            state.timestamp,
            state.traderData,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append([listing["symbol"], listing["product"], listing["denomination"]])

        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([
                    trade.symbol,
                    trade.price,
                    trade.quantity,
                    trade.buyer,
                    trade.seller,
                    trade.timestamp,
                ])

        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sunlight,
                observation.humidity,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

logger = Logger()

class Trader:
    def updateTraderData(self, state: TradingState, trader_data: Dict[str, Any]) -> dict[str, Any]:
        
        for product in trader_data:
            if trader_data[product]["price_method"] == "static":
                pass

            elif trader_data[product]["price_method"] == "average":
                assert product in state.order_depths

                best_bid = list(state.order_depths[product].buy_orders.keys())[0]
                best_ask = list(state.order_depths[product].sell_orders.keys())[0]
                trader_data[product]["price_data"].append((best_bid + best_ask) / 2)
                
                if len(trader_data[product]["price_data"]) > trader_data[product]["price_data_size"]:
                    trader_data[product]["price_data"].pop(0)
                elif len(trader_data[product]["price_data"]) < trader_data[product]["price_data_size"]:
                    continue

                trader_data[product]["mid_price"] = round(sum(trader_data[product]["price_data"]) / len(trader_data[product]["price_data"]))
                trader_data[product]["buy_price"] = trader_data[product]["mid_price"] + trader_data[product]["price_spread"][0]
                trader_data[product]["sell_price"] = trader_data[product]["mid_price"] + trader_data[product]["price_spread"][1]
                trader_data[product]['excess_buy'] = [(trader_data[product]["buy_price"], 1.)]
                trader_data[product]['excess_sell'] = [(trader_data[product]["sell_price"], 1.)]
            
        return trader_data

    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]:        
        result = {}
        conversions = 0
        
        # Initialize traderData in the first iteration
        if state.traderData == "":
            trader_data_prev = TRADER_DATA
        else:
            trader_data_prev = jsonpickle.decode(state.traderData)

        # Update trader data with new information
        trader_data =  self.updateTraderData(state, trader_data_prev)

        for product in state.order_depths:
            
            order_depth = state.order_depths[product]
            position = state.position.get(product, 0)
            position_limit = trader_data[product]["position_limit"]
            position_stage_1 = trader_data[product]["position_stage_1"]
            position_stage_2 = trader_data[product]["position_stage_2"]

            buy_power, sell_power = position_limit - position, position_limit + position
            num_buy = num_sell = 0
            buy_orders, sell_orders = defaultdict(int), defaultdict(int)

            """
            Market taker: Try to find profitable orders in the order depths
            """

            # Try to match all buy orders with sell orders if prices are above sell price
            outstanding_buy_orders = list(order_depth.buy_orders.items())
            if trader_data[product]["sell_price"] is not None:
                i = 0
                while sell_power > num_sell and i < len(outstanding_buy_orders) and \
                         outstanding_buy_orders[i][0] >= trader_data[product]["sell_price"]:
                                                          
                    bid, bid_amount = outstanding_buy_orders[i]
                    sell_amount = min(bid_amount, sell_power - num_sell)
                    sell_orders[bid] += sell_amount
                    num_sell += sell_amount
                    outstanding_buy_orders[i] = bid, bid_amount - sell_amount
                    i += 1
            
            # If position is still above stage 1, try to sell excess at above mid price
            if trader_data[product]["mid_price"] is not None and num_sell == 0:
                while (position - num_sell > position_stage_1) and i < len(outstanding_buy_orders) and \
                         outstanding_buy_orders[i][0] >= trader_data[product]["mid_price"]:
                    
                    bid, bid_amount = outstanding_buy_orders[i]
                    sell_amount = min([bid_amount, position - num_sell - position_stage_1])
                    if sell_amount > 0:                        
                        sell_orders[bid] += sell_amount
                        num_sell += sell_amount
                        outstanding_buy_orders[i] = bid, bid_amount - sell_amount
                    i += 1
            
            # Try to match all sell orders with buy orders if prices are below buy price
            outstanding_sell_orders = list(order_depth.sell_orders.items())
            if trader_data[product]["buy_price"] is not None:
                i = 0
                while buy_power > num_buy and i < len(outstanding_sell_orders) and \
                         outstanding_sell_orders[i][0] <= trader_data[product]["buy_price"]:
                    
                    ask, ask_amount = outstanding_sell_orders[i]
                    buy_amount = min(-ask_amount, buy_power - num_buy)
                    buy_orders[ask] += buy_amount
                    num_buy += buy_amount
                    outstanding_sell_orders[i] = ask, ask_amount + buy_amount
                    i += 1

            # If position is still below - stage 1, try to buy excess at below mid price
            if trader_data[product]["mid_price"] is not None and num_buy == 0:
                i = 0
                while (position + num_buy < -position_stage_1) and i < len(outstanding_sell_orders) and \
                         outstanding_sell_orders[i][0] <= trader_data[product]["mid_price"]:
                    
                    ask, ask_amount = outstanding_sell_orders[i]
                    buy_amount = min([-ask_amount, -position - num_buy - position_stage_1])
                    if buy_amount > 0:
                        buy_orders[ask] += buy_amount
                        num_buy += buy_amount
                        outstanding_sell_orders[i] = ask, ask_amount + buy_amount
                    i += 1

            """
            Market maker: Place buy and sell orders at certain price levels
            """

            # If position is above stage 2 and no good order is found in market, try to sell excess at mid price
            # If position is below - stage 2 and no good order is found in market, try to buy excess at mid price
            if position > position_stage_2 and num_sell == 0 and trader_data[product]["mid_price"] is not None:
                sell_orders[trader_data[product]["mid_price"]] += position - position_stage_2
                num_sell += position - position_stage_2
            elif position < -position_stage_2 and num_buy == 0 and trader_data[product]["mid_price"] is not None:
                buy_orders[trader_data[product]["mid_price"]] += -position - position_stage_2
                num_buy += -position - position_stage_2

            if trader_data[product]["excess_buy"] is not None:
                for buy_price, buy_fraction in trader_data[product]["excess_buy"]:
                    buy_quantity = int(buy_fraction * (buy_power - num_buy))
                    if buy_quantity > 0:
                        buy_orders[buy_price] += buy_quantity
                        num_buy += buy_quantity

            if trader_data[product]["excess_sell"] is not None:
                for sell_price, sell_fraction in trader_data[product]["excess_sell"]:
                    sell_quantity = int(sell_fraction * (sell_power - num_sell))
                    if sell_quantity > 0:
                        sell_orders[sell_price] += sell_quantity
                        num_sell += sell_quantity

            """
            Format buy_orders and sell_orders into Order objects
            """
            orders = []
            # for price, amount in sorted(list(buy_orders.items()), key=lambda x: x[0]):
            #     orders.append(Order(product, price, amount))
            # for price, amount in sorted(list(sell_orders.items()), key=lambda x: x[0], reverse=True):
            #     orders.append(Order(product, price, -amount))

            if ORDER:
                for price, amount in sorted(list(buy_orders.items()), key=lambda x: x[0], reverse=True):
                    orders.append(Order(product, price, amount))
                for price, amount in sorted(list(sell_orders.items()), key=lambda x: x[0]):
                    orders.append(Order(product, price, -amount))
            else:
                for price, amount in sorted(list(buy_orders.items()), key=lambda x: x[0]):
                    orders.append(Order(product, price, amount))
                for price, amount in sorted(list(sell_orders.items()), key=lambda x: x[0], reverse=True):
                    orders.append(Order(product, price, -amount))

            logger.print(orders)
            result[product] = orders

        # Format the output
        trader_data = jsonpickle.encode(trader_data)

        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data