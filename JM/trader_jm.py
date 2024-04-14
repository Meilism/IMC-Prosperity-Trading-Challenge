import json, jsonpickle
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any, List, Dict

PRODUCTS = [
    "AMETHYSTS",
    "STARFRUIT",
    # "ORCHIDS",
]

TRADER_DATA = {
    'AMETHYSTS': {

        'POS_LIMIT': 20,
        'num_buy': 0,
        'num_sell': 0,

        'price_method': 'static',
        'strategy': ['market_take', 'market_make'],
        'expected_mid_price': 10000,

        'take_position_stage': [0, 20],
        'take_price_spread': [(2, 2), (2, 0)],

        'make_position_stage': [0, 15, 20],
        'make_price_spread': [(2, 2), (2, 1), (2, 0)],
        'make_price_offset': [1, 1],

    },
    
    'STARFRUIT': {

        'POS_LIMIT': 20,
        'num_buy': 0,
        'num_sell': 0,

        'strategy': ['market_take', 'market_make'],

        # Data and parameters specific for mid_price calculation: method = "MA_1
        'price_method': 'MA_1',
        'expected_mid_price': None, 
        'MA_coef': -0.7086,
        'mid_price_data': [],
        'price_data_size': 1,

        # Data and parameters specific for mid_price calculation: method = "average"
        # 'price_method': 'average',
        # 'expected_mid_price': None,
        # 'mid_price_data': [],
        # 'price_data_size': 8,

        # Data and parameters specific for mid_price calculation: method = "weighted_average"
        # 'price_method': 'weighted_average',
        # 'expected_mid_price': None,
        # 'weights': [],

        'take_position_stage': [0, 20],
        'take_price_spread': [(1, 1), (1, 0)],

        'make_position_stage': [20],
        'make_price_spread': [(1, 1)],
        'make_price_offset': [1, 1],

    },

    'ORCHIDS': {

        'POS_LIMIT': 100,
        'price_method': 'static',
        'strategy': ['local_sell_take', 'local_sell_make' 'foreign_buy'],

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

    def updatePrice(self, state: TradingState, product: Symbol, data: Dict[str, Any]) -> None:
        # Update mid_price_data
        best_ask = list(state.order_depths[product].sell_orders.items())[0][0]
        best_bid = list(state.order_depths[product].buy_orders.items())[0][0]
        mid_price = (best_ask + best_bid) / 2

        data['mid_price_data'].append(mid_price)
        if len(data['mid_price_data']) > data['price_data_size']:
            data['mid_price_data'].pop(0)



    def calculateAverage(self, data: list[int], weights: list[float]|None) -> int:
        if weights:
            return sum([data[i] * weights[i] for i in range(len(data))])/sum(weights)
        return sum(data) / len(data)



    def getPriceSpread(self, position:int, stage:tuple[int], spread:tuple[tuple[int, int]]) -> tuple[int, int]:
        sign = 1 if position >= 0 else -1
        for i, pos in enumerate(stage):
            if abs(position) <= pos:
                return spread[i][::sign]
            


    def updateTraderData(self, state: TradingState, trader_data: Dict[Symbol, Dict[str, Any]]) -> None:
        for product in trader_data:
            data = trader_data[product]
            data['num_buy'] = data['num_sell'] = 0
            
            if data['price_method'] == 'static':
                continue

            
            # Moving Average 1 model to predict mid_price
            if data['price_method'] == 'MA_1':
                
                self.updatePrice(state, product, data)
                if data['expected_mid_price'] is None:
                    data['expected_mid_price'] = data['mid_price_data'][-1]
                else:
                    d = data['MA_coef'] * (data['mid_price_data'][-1] - data['expected_mid_price'])
                    data['expected_mid_price'] = data['mid_price_data'][-1] + d


            # Simple Average model to predict mid_price
            elif data['price_method'] == 'average':

                self.updatePrice(state, product, data)
                if len(data['mid_price_data']) == data['price_data_size']:
                    data['expected_mid_price'] = self.calculateAverage(data['mid_price_data'], None)


            # Weighted Average model to predict mid_price
            elif data['price_method'] == 'weighted_average':
                pass


            elif data['price_method'] == 'average_with_trend':
                pass



    def computeTakeOrders(self, product: Symbol, state: TradingState, data: Dict[str, Any]) -> list[Order]:
        if data['expected_mid_price'] is None:
            return []

        orders = []
        buy_orders, sell_orders = state.order_depths[product].buy_orders.items(), state.order_depths[product].sell_orders.items()
        POS_LIMIT, position = data['POS_LIMIT'], state.position.get(product, 0)
        
        buy_offset, sell_offset = self.getPriceSpread(position + data['num_buy'] - data['num_sell'], 
                                                      data['take_position_stage'], 
                                                      data['take_price_spread'])
        
        acc_ask = data['expected_mid_price'] - buy_offset # price to buy, lower the better
        acc_bid = data['expected_mid_price'] + sell_offset # price to sell, higher the better

        for ask, ask_amount in sell_orders:
            if (ask <= acc_ask) and (data['num_buy'] < POS_LIMIT - position):
                buy_amount = min(-ask_amount, POS_LIMIT - position - data['num_buy'])
                orders.append(Order(product, ask, buy_amount))
                data['num_buy'] += buy_amount

        for bid, bid_amount in buy_orders:
            if (bid >= acc_bid) and (data['num_sell'] < POS_LIMIT + position):
                sell_amount = min(bid_amount, POS_LIMIT + position - data['num_sell'])
                orders.append(Order(product, bid, -sell_amount))
                data['num_sell'] += sell_amount

        return orders
    


    def computeMakeOrders(self, product: Symbol, state: TradingState, data: Dict[str, Any]) -> list[Order]:
        if data['expected_mid_price'] is None:
            return []
        
        orders = []
        best_bid = list(state.order_depths[product].buy_orders.items())[0][0]
        best_ask = list(state.order_depths[product].sell_orders.items())[0][0]
        position = state.position.get(product, 0)

        buy_offset, sell_offset = self.getPriceSpread(position + data['num_buy'] - data['num_sell'], 
                                                      data['make_position_stage'], 
                                                      data['make_price_spread'])

        our_bid = min(best_bid + buy_offset, data['expected_mid_price'] - data['make_price_offset'][0])
        our_ask = max(best_ask - sell_offset, data['expected_mid_price'] + data['make_price_offset'][1])
        buy_amount = data['POS_LIMIT'] - position - data['num_buy']
        sell_amount = data['POS_LIMIT'] + position - data['num_sell']
        
        if buy_amount > 0:
            orders.append(Order(product, our_bid, buy_amount))
            data['num_buy'] += buy_amount

        if sell_amount > 0:
            orders.append(Order(product, our_ask, -sell_amount))
            data['num_sell'] += sell_amount
        
        return orders
    


    def computeLocalSellTakeOrders(self, product: Symbol, state: TradingState, data: Dict[str, Any]) -> list[Order]:
        orders = []
        return orders
    


    def computeLocalSellMakeOrders(self, product: Symbol, state: TradingState, data: Dict[str, Any]) -> list[Order]:
        orders = []
        return orders
    


    def computeForeignBuyOrders(self, product: Symbol, state: TradingState, data: Dict[str, Any]) -> int:
        conversions = 0
        return conversions
    


    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]: 
        
        # Initialize returned variables
        result = {}
        conversions = 0
        
        # Initialize traderData in the first iteration
        if state.traderData == "":
            trader_data = TRADER_DATA
        else:
            trader_data = jsonpickle.decode(state.traderData)

        # Update trader data with new information and apply pricing models
        self.updateTraderData(state, trader_data)

        for product in PRODUCTS:
            orders = []

            for strategy in trader_data[product]["strategy"]:

                if strategy == "market_take":
                    orders += self.computeTakeOrders(product, state, trader_data[product])
                    
                elif strategy == "market_make":
                    orders += self.computeMakeOrders(product, state, trader_data[product])
                
                elif strategy == "local_sell_take":
                    orders += self.computeLocalSellTakeOrders(product, state, trader_data[product])

                elif strategy == "local_sell_make":
                    orders += self.computeLocalSellMakeOrders(product, state, trader_data[product])

                elif strategy == "foreign_buy":
                    conversions = self.computeForeignBuyOrders(product, state, trader_data[product])

            result[product] = orders

        # Format the output
        trader_data = jsonpickle.encode(trader_data)

        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data    