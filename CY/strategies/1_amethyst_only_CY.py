import json, jsonpickle
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any, List

TRADER_DATA = {
    'AMETHYSTS': {
        'position_limit': 20,
        'buy_price': [(9998, 0.8), (9996, 0.2)],
        'sell_price': [(10002, 0.8), (10004, 0.2)],
    },
    'STARFRUIT': {
        'position_limit': 20,
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
        Strategy for trading AMETHYSTS
        """

        current_position = state.position.get("AMETHYSTS",0)
        position_limit = trader_data_prev["AMETHYSTS"]["position_limit"]
        orders = []

        # Place buy and sell orders
        for buy_price, position in trader_data_prev["AMETHYSTS"]["buy_price"]:
            buy_quantity = int(position * (position_limit - current_position))
            if buy_quantity > 0:
                buy_order = Order("AMETHYSTS", buy_price, buy_quantity)
                orders.append(buy_order)
        for sell_price, position in trader_data_prev["AMETHYSTS"]["sell_price"]:
            sell_quantity = int(position * (position_limit + current_position))
            if sell_quantity > 0:
                sell_order = Order("AMETHYSTS", sell_price, -sell_quantity)
                orders.append(sell_order)

        result['AMETHYSTS'] = orders

        """
        TODO: Strategy for trading STARFRUIT
        """

        # Format the output
        trader_data = jsonpickle.encode(trader_data_prev)

        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data