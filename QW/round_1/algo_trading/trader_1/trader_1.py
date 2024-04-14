from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any
import numpy as np
import jsonpickle, json

class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        base_length = len(self.to_json([
            self.compress_state(state, ""),
            self.compress_orders(orders),
            conversions,
            "",
            "",
        ]))

        # We truncate state.traderData, trader_data, and self.logs to the same max. length to fit the log limit
        max_item_length = (self.max_log_length - base_length) // 3

        print(self.to_json([
            self.compress_state(state, self.truncate(state.traderData, max_item_length)),
            self.compress_orders(orders),
            conversions,
            self.truncate(trader_data, max_item_length),
            self.truncate(self.logs, max_item_length),
        ]))

        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
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

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        if len(value) <= max_length:
            return value

        return value[:max_length - 3] + "..."

logger = Logger()

class Trader:

    def __init__(self) -> None:
        pass

    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        # print("traderData: " + state.traderData)
        # print("Observations: " + str(state.observations))

        if state.traderData == "":
            trader_data: dict[str, list[int]] = {"AMETHYSTS":[], "STARFRUIT":[]}
        else:
            trader_data = jsonpickle.decode(state.traderData)

        position_limit = 20
        samp_size = 10
        result = {}
        for product, order_depth in state.order_depths.items():
            orders: list[Order] = []

            if len(order_depth.buy_orders) == 0 or len(order_depth.sell_orders) == 0:
                continue

            # bid_prices = list(order_depth.buy_orders.keys())
            # bid_quantities = list(order_depth.buy_orders.values())
            # bid_ave_price = np.average(bid_prices, weights=bid_quantities)

            # ask_prices = list(order_depth.sell_orders.keys())
            # ask_quantities = list(order_depth.sell_orders.values())
            # ask_ave_price = np.average(ask_prices, weights=ask_quantities)

            # mid_price = (bid_ave_price + ask_ave_price) / 2

            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]

            mid_price = (best_ask + best_bid) / 2

            trader_data[product].append(mid_price)
            trader_data[product] = trader_data[product][-samp_size:] # only keep the last samp_size elements to avoid memory overflow

            if len(trader_data[product]) < samp_size:
                continue
            
            d_list = np.diff(trader_data[product])
            d = d_list[-1]*(-0.7073) + d_list[-2]*(-0.4919) + d_list[-3]*(-0.3443) + d_list[-4]*(-0.2347) + d_list[-5]*(-0.1374) + d_list[-6]*(-0.0612) # use ARIMA (5,1,0) coefficients
            acceptable_price = mid_price + d
            
            # best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            if best_ask < acceptable_price:
                orders.append(Order(product, best_ask, 1))
            # else:
            #     orders.append(Order(product, int(np.floor(acceptable_price-1)), 1))

            # best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            if best_bid > acceptable_price:
                orders.append(Order(product, best_bid, -1))
            # else:
            #     orders.append(Order(product, int(np.ceil(acceptable_price+1)), -1))

            result[product] = orders

        conversions = 1
        trader_data = jsonpickle.encode(trader_data)
        logger.flush(state, result, conversions, trader_data)

        return result, conversions, trader_data