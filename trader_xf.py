import json
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any, List
import jsonpickle

POSITION_LIMIT = {
	"AMETHYSTS": 20,
	"STARFRUIT": 20,
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
    
    def run(self,state: TradingState):
        #print("traderData: " + state.traderData)
        #print("Observations: " + str(state.observations))
        
        
        
        
        if state.traderData == "":
            productaverage={}
				# Orders to be placed on exchange matching engine
        else:
            productaverage = jsonpickle.decode(state.traderData)
        result = {}
    
      #  print("position:",state.position,'||||||')
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
                
            
            if product not in productaverage:
                productaverage[product] =[]
            if len(productaverage[product]) < 5:
                acceptablebuy_price = 0
                acceptablesell_price = 100000000
            else:
                acceptablebuy_price = sum(productaverage[product])/len(productaverage[product])
                acceptablesell_price = acceptablebuy_price
            Sumprice = 0
            totalnum = 0
            cur_position = state.position.get(product, 0)  
            logger.print("Acceptable price : " + str(acceptablebuy_price))
            
        
        
        #   print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
            if len(order_depth.sell_orders) != 0:
                
                Sell_Order = sorted(list(order_depth.sell_orders.items()), key=lambda x: x[0]  )
            
                
                for ask, amount in Sell_Order: ##amount is negative we want to buy
                    if ask < acceptablebuy_price: ##buy
                    #    print('kk')
                        if cur_position < 20:
                            buyamount = min(20-cur_position,-amount)
                            cur_position += buyamount
                            logger.print("BUY", str(buyamount) + "x", ask)
                            orders.append(Order(product, ask, buyamount)) 
                    Sumprice += ask*(-amount)
                    totalnum += -amount
                    
        
            if len(order_depth.buy_orders) != 0: ##someone in market want to buy, we want to sell them
                
                Buy_Order = sorted(list(order_depth.buy_orders.items()), key=lambda x: -x[0]  )
            
                for bid, amount in Buy_Order: ##amount is postive number, we want to sell
                    if bid > acceptablesell_price: ##sell
                        if cur_position >-20: 
                            sellamount = min(cur_position+20, amount) ## sellamount is a postive number
                            cur_position -= sellamount ## after sell need to subtract it
                            logger.print("SELL", str(sellamount) + "x", bid)
                            orders.append(Order(product, bid, -sellamount))
                    Sumprice += bid*(amount)
                    totalnum += amount
                              
                    
            productaverage[product].append(Sumprice/totalnum)
            if len(productaverage[product])==6:
                productaverage[product].pop(0)
            
            result[product] = orders
        #print(state.position)
        traderData = jsonpickle.encode(productaverage)  
        #state.traderData = traderData
        #traderData = state.traderData
        #print('******'+traderData+'********')
				# Sample conversion request. Check more details below. 
        conversions = 1
        logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData




