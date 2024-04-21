import json, jsonpickle
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any, List, Dict
import collections, copy
from collections import defaultdict
import numpy as np


empty_dict = {'STRAWBERRIES' : 0, 'CHOCOLATE': 0, 'ROSES' : 0, 'GIFT_BASKET' : 0}

def def_value():
    return copy.deepcopy(empty_dict)

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

    position = copy.deepcopy(empty_dict)
    POSITION_LIMIT = {'STRAWBERRIES' : 350, 'CHOCOLATE': 250, 'ROSES' : 60, 'GIFT_BASKET' : 60}

    person_position = defaultdict(def_value)

    basket_std = 76.4
    basket_diff = 379.5

    def compute_orders_basket(self, order_depth, pair_price_diff_last):

        orders = {'STRAWBERRIES' : [], 'CHOCOLATE': [], 'ROSES' : [], 'GIFT_BASKET' : []}
        prods = ['STRAWBERRIES', 'CHOCOLATE', 'ROSES', 'GIFT_BASKET']
        best_sell, best_buy, best_buy_vol, best_sell_vol, mid_price = {}, {}, {}, {}, {}

        for p in prods:
            best_sell[p], best_sell_vol[p] = list(order_depth[p].sell_orders.items())[0]
            best_buy[p], best_buy_vol[p] = list(order_depth[p].buy_orders.items())[0]

            mid_price[p] = (best_sell[p] + best_buy[p])/2

        pair_price_diff = mid_price['GIFT_BASKET'] - mid_price['STRAWBERRIES']*6 - mid_price['CHOCOLATE']*4 - mid_price['ROSES']

        if pair_price_diff_last == 0:
            return pair_price_diff, orders

        fair_price = pair_price_diff*0.9231 + pair_price_diff_last*0.0738

        res_sell = best_buy['GIFT_BASKET'] - best_sell['STRAWBERRIES']*6 - best_sell['CHOCOLATE']*4 - best_sell['ROSES'] - fair_price
        res_buy = - (best_sell['GIFT_BASKET'] - best_buy['STRAWBERRIES']*6 - best_buy['CHOCOLATE']*4 - best_buy['ROSES']) + fair_price

        trade_at = self.basket_std*0.0

        print(res_sell, res_buy, trade_at, pair_price_diff, pair_price_diff_last, fair_price)

        if res_sell > trade_at:

            vol_basket = min(self.POSITION_LIMIT['GIFT_BASKET'] + self.position['GIFT_BASKET'], best_buy_vol['GIFT_BASKET'])
            vol_straw = min(self.POSITION_LIMIT['STRAWBERRIES'] - self.position['STRAWBERRIES'], -best_sell_vol['STRAWBERRIES'])
            vol_choc = min(self.POSITION_LIMIT['CHOCOLATE'] - self.position['CHOCOLATE'], -best_sell_vol['CHOCOLATE'])
            vol_roses = min(self.POSITION_LIMIT['ROSES'] - self.position['ROSES'], -best_sell_vol['ROSES'])

            vol = int(min(vol_basket, vol_straw/6, vol_choc/4, vol_roses))

            orders['GIFT_BASKET'].append(Order('GIFT_BASKET', best_buy['GIFT_BASKET'], -vol)) 
            orders['STRAWBERRIES'].append(Order('STRAWBERRIES', best_sell['STRAWBERRIES'], vol*6))
            orders['CHOCOLATE'].append(Order('CHOCOLATE', best_sell['CHOCOLATE'], vol*4))
            orders['ROSES'].append(Order('ROSES', best_sell['ROSES'], vol))

        elif res_buy > trade_at:
            vol_basket = min(self.POSITION_LIMIT['GIFT_BASKET'] - self.position['GIFT_BASKET'], -best_sell_vol['GIFT_BASKET'])
            vol_straw = min(self.POSITION_LIMIT['STRAWBERRIES'] + self.position['STRAWBERRIES'], best_buy_vol['STRAWBERRIES'])
            vol_choc = min(self.POSITION_LIMIT['CHOCOLATE'] + self.position['CHOCOLATE'], best_buy_vol['CHOCOLATE'])
            vol_roses = min(self.POSITION_LIMIT['ROSES'] + self.position['ROSES'], best_buy_vol['ROSES'])

            vol = int(min(vol_basket, vol_straw/6, vol_choc/4, vol_roses))

            orders['GIFT_BASKET'].append(Order('GIFT_BASKET', best_sell['GIFT_BASKET'], vol))
            orders['STRAWBERRIES'].append(Order('STRAWBERRIES', best_buy['STRAWBERRIES'], -vol*6))
            orders['CHOCOLATE'].append(Order('CHOCOLATE', best_buy['CHOCOLATE'], -vol*4))
            orders['ROSES'].append(Order('ROSES', best_buy['ROSES'], -vol))


        # vol_basket = self.POSITION_LIMIT['GIFT_BASKET'] + self.position['GIFT_BASKET']
        # vol_straw = self.POSITION_LIMIT['STRAWBERRIES'] - self.position['STRAWBERRIES']
        # vol_choc = self.POSITION_LIMIT['CHOCOLATE'] - self.position['CHOCOLATE']
        # vol_roses = self.POSITION_LIMIT['ROSES'] - self.position['ROSES']

        # vol = int(min(vol_basket, vol_straw/6, vol_choc/4, vol_roses)/10)

        # orders['GIFT_BASKET'].append(Order('GIFT_BASKET', round(mid_price['GIFT_BASKET'])+1, -vol)) 
        # orders['STRAWBERRIES'].append(Order('STRAWBERRIES', round(mid_price['STRAWBERRIES'])-1, vol*6))
        # orders['CHOCOLATE'].append(Order('CHOCOLATE', round(mid_price['CHOCOLATE'])-1, vol*4))
        # orders['ROSES'].append(Order('ROSES', round(mid_price['ROSES'])-1, vol))

        # vol_basket = self.POSITION_LIMIT['GIFT_BASKET'] - self.position['GIFT_BASKET']
        # vol_straw = self.POSITION_LIMIT['STRAWBERRIES'] + self.position['STRAWBERRIES']
        # vol_choc = self.POSITION_LIMIT['CHOCOLATE'] + self.position['CHOCOLATE']
        # vol_roses = self.POSITION_LIMIT['ROSES'] + self.position['ROSES']

        # vol = int(min(vol_basket, vol_straw/6, vol_choc/4, vol_roses)/10)

        # orders['GIFT_BASKET'].append(Order('GIFT_BASKET', round(best_sell['GIFT_BASKET'])-1, vol))
        # orders['STRAWBERRIES'].append(Order('STRAWBERRIES', round(best_buy['STRAWBERRIES'])+1, -vol*6))
        # orders['CHOCOLATE'].append(Order('CHOCOLATE', round(best_buy['CHOCOLATE'])+1, -vol*4))
        # orders['ROSES'].append(Order('ROSES', round(best_buy['ROSES'])+1, -vol))

        return pair_price_diff, orders

    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]: 
        
        # Initialize returned variables
        if state.traderData == "":
            trader_data = 0
        else:
            trader_data = jsonpickle.decode(state.traderData)

        conversions = 0
        result = {'STRAWBERRIES' : [], 'CHOCOLATE' : [], 'ROSES' : [], 'GIFT_BASKET' : []}

        for key, val in state.position.items():
            if key in result.keys():
                self.position[key] = val

        pair_price_diff, orders = self.compute_orders_basket(state.order_depths, trader_data)
        result['GIFT_BASKET'] += orders['GIFT_BASKET']
        result['STRAWBERRIES'] += orders['STRAWBERRIES']
        result['CHOCOLATE'] += orders['CHOCOLATE']
        result['ROSES'] += orders['ROSES']

        # Format the output
        trader_data = jsonpickle.encode(pair_price_diff)

        # logger.flush(state, result, conversions, trader_data)
        logger.print(result)

        return result, conversions, trader_data    