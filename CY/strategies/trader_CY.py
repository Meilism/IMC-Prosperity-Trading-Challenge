import json, jsonpickle
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any, List

POSITION_LIMIT = {
    'AMETHYSTS': 20,
    'STARFRUIT': 20,
}

TRADER_DATA = {
    'AMETHYSTS': {
        'acceptable_price': 10000,
        'buy_fraction': [(-2, 0.6), (-4, 0.2), (-5, 0.1)],
        'sell_fraction': [(2, 0.6), (4, 0.2), (5, 0.1)],
    },
    'STARFRUIT': {

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
    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]:
        result = {}
        conversions = 0
        trader_data = ""
        # Initialize traderData in the first iteration
        if state.traderData == "":
            trader_data_prev = TRADER_DATA
        else:
            trader_data_prev = jsonpickle.decode(state.traderData)

        """
        Strategy for trading AMETHYSTS: static market making
        """

        position = state.position.get("AMETHYSTS",0)
        position_limit = POSITION_LIMIT["AMETHYSTS"]
        buy_limit = position_limit - position
        sell_limit = position_limit + position
        orders = []

        # "Market taker": Look at order depths to find profitable trades
        order_depth = state.order_depths.get("AMETHYSTS", None)
        if order_depth:
            if len(order_depth.buy_orders) > 0:
                for bid, bid_amount in order_depth.buy_orders.items():
                    if bid > trader_data_prev["AMETHYSTS"]["acceptable_price"]:
                        bid_amount = min(bid_amount, sell_limit)
                        orders.append(Order("AMETHYSTS", bid, -bid_amount))
                        sell_limit -= bid_amount
                    else:
                        break
        
            if len(order_depth.sell_orders) > 0:
                for ask, ask_amount in order_depth.sell_orders.items():
                    if ask < trader_data_prev["AMETHYSTS"]["acceptable_price"]:
                        ask_amount = min(-ask_amount, buy_limit)
                        orders.append(Order("AMETHYSTS", ask, ask_amount))
                        buy_limit -= ask_amount
                    else:
                        break

        # "Market maker": Place buy and sell orders at certain price levels
        for buy_price_diff, buy_fraction in trader_data_prev["AMETHYSTS"]["buy_fraction"]:
            buy_quantity = int(buy_fraction * buy_limit)
            if buy_quantity > 0:
                buy_order = Order("AMETHYSTS", buy_price_diff + trader_data_prev["AMETHYSTS"]["acceptable_price"], buy_quantity)
                orders.append(buy_order)

        for sell_price_diff, sell_fraction in trader_data_prev["AMETHYSTS"]["sell_fraction"]:
            sell_quantity = int(sell_fraction * sell_limit)
            if sell_quantity > 0:
                sell_order = Order("AMETHYSTS", sell_price_diff + trader_data_prev["AMETHYSTS"]["acceptable_price"], -sell_quantity)
                orders.append(sell_order)

        result['AMETHYSTS'] = orders

        """
        TODO: Strategy for trading STARFRUIT
        """

        position = state.position.get("STARFRUIT",0)
        position_limit = POSITION_LIMIT["STARFRUIT"]
        buy_limit = position_limit - position
        sell_limit = position_limit + position
        orders = []

        # "Market taker": Look at order depths to find profitable trades
        

        # "Market maker": Place buy and sell orders at certain price levels


        # Format the output
        trader_data = jsonpickle.encode(trader_data_prev)
            
        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data