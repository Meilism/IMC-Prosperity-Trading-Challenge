#!/usr/bin/env python
# coding: utf-8

# In[12]:


import json
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any, List
import jsonpickle
import numpy as np

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
    
    def __init__(self) -> None:
        self.product_infor = {}
        self.maxlookback = 10

    def movingaverage(self, name, product, cat , expparameter = 0 ):
        rawweight = np.linspace(1,len(self.product_infor[product][cat]), len(self.product_infor[product][cat]))
        if name == 'Linear':
            weight = rawweight + expparameter 
        elif name == 'Exp':
            weight = np.exp(expparameter*rawweight ) ##exp(weight*para) if para ==0, then this is equal weighting moving average
        acceptable_price = sum(np.array(self.product_infor[product][cat]) * weight)/sum(weight)
        return acceptable_price
    def LinearRegression(self,product,cat):
        x = np.linspace(1,len(self.product_infor[product][cat]), len(self.product_infor[product][cat]))
        m,b = np.polyfit(x,self.product_infor[product][cat],1)
        return  m, b
    
    def midprice_spread(self,  buyorder = [], sellorder = [],Weighted_mid =True):
        if len(buyorder) == 0 and len(sellorder) ==0:
            return 'No_Mid'
        elif len(buyorder) != 0 and len(sellorder) == 0:
            bestbuy = buyorder[0][0]
            bestsell = bestbuy
        elif len(buyorder) == 0 and len(sellorder) != 0:
            bestsell = sellorder[0][0]
            bestbuy = bestsell
        else:
            bestbuy, bestsell = buyorder[0][0], sellorder[0][0]
        if Weighted_mid == True:
            midprice = (len(buyorder)*bestsell+len(sellorder)*bestbuy)/(len(buyorder)+ len(sellorder))
        else:
            midprice = (bestbuy + bestsell)/2
        return midprice, bestsell - bestbuy 
                    

    def estimate_basket(self, state):
        MIDPRICE={'ROSES':0, 'STRAWBERRIES':0,'CHOCOLATE':0, 'GIFT_BASKET':0 }
        EST_MIDPRICE={'ROSES':0, 'STRAWBERRIES':0,'CHOCOLATE':0, 'GIFT_BASKET':0 }
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            
            Sell_Order = sorted(list(order_depth.sell_orders.items()), key=lambda x: x[0]  )
            Buy_Order = sorted(list(order_depth.buy_orders.items()), key=lambda x: -x[0]  )

            bestsell = Sell_Order[0][0]
            bestbuy = Buy_Order[0][0]

            midprice = (bestsell+bestbuy)/2
            MIDPRICE[product] = midprice
          #  Logger.print( MIDPRICE['CHOCOLATE']*4+MIDPRICE['STRAWBERRIES']*6+MIDPRICE['ROSES']+379.49 - MIDPRICE['GIFT_BASKET']   )

        EST_MIDPRICE['GIFT_BASKET'] =   MIDPRICE['CHOCOLATE']*4+MIDPRICE['STRAWBERRIES']*6+MIDPRICE['ROSES']+379.49
        EST_MIDPRICE['ROSES'] = (MIDPRICE['GIFT_BASKET'] -  MIDPRICE['CHOCOLATE']*4-MIDPRICE['STRAWBERRIES']*6 - 379.49)
        EST_MIDPRICE['CHOCOLATE'] =  (MIDPRICE['GIFT_BASKET'] -  MIDPRICE['ROSES']-MIDPRICE['STRAWBERRIES']*6 - 379.49)/4
        EST_MIDPRICE['STRAWBERRIES'] = (MIDPRICE['GIFT_BASKET'] -  MIDPRICE['CHOCOLATE']*4-MIDPRICE['ROSES'] - 379.49)/6
        return EST_MIDPRICE

        ##76.42
    def run(self,state: TradingState):
        #print("traderData: " + state.traderData)
        #print("Observations: " + str(state.observations))
        traderData = ""
        POSITION_LIMIT = {'ROSES':60, 'STRAWBERRIES':350,'CHOCOLATE':250, 'GIFT_BASKET':60}
        

        if state.traderData != "":
            self.product_infor = jsonpickle.decode(state.traderData)
        result = {}
    
      #  print("position:",state.position,'||||||')
   
        EST_MIDPRICE = self.estimate_basket(state)
        EST_MIDSTD = {'ROSES':76.42, 'STRAWBERRIES':76.42/6,'CHOCOLATE':76.42/4, 'GIFT_BASKET':76.42*0}
        for product in state.order_depths:
            if product not in POSITION_LIMIT:
                continue
            if product not in self.product_infor:
                    self.product_infor[product] ={'mean':[],'std':[],'mid':[],'spread':[],'buy':[],'sell':[]}
            position_limit = POSITION_LIMIT[product]

            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            if product != 'GIFT_BASKET11':
                acceptablebuy_price = EST_MIDPRICE[product]-EST_MIDSTD[product]
                acceptablesell_price = EST_MIDPRICE[product]+EST_MIDSTD[product]
                weighted = False
                timeskip = 1
            else:
                pricetype = 'mean'  ##mid, mean
                spreadtype = 'std' ##std, spread
                prefactor1 = 0.8
                prefactor2 = 0.8
                weighted = False ##weighted mid

                self.maxlookback = 2
                timeskip = 1
                MovingAverageType = 'Exp'  ##Linear, Exp
                MovingParameters = 0 ## 0 for linear


            
                
                if len(self.product_infor[product][pricetype]) < self.maxlookback:
                    acceptablebuy_price = 0
                    acceptablesell_price = 100000000
                else:
                    # acceptablebuy_price = self.movingaverage(MovingAverageType, product,pricetype,MovingParameters)
                    # acceptablesell_price = acceptablebuy_price
                    m,b = self.LinearRegression(product,pricetype)

                    acceptablebuy_price = (len(self.product_infor[product][pricetype])+1)*m+b
                    acceptablesell_price = acceptablebuy_price
                    Sell_Order = sorted(list(order_depth.sell_orders.items()), key=lambda x: x[0]  )
                    Buy_Order = sorted(list(order_depth.buy_orders.items()), key=lambda x: -x[0]  )
                    if state.timestamp%timeskip ==0:
                        if m>0:
                            acceptablebuy_price = acceptablebuy_price
                            acceptablesell_price = acceptablebuy_price+1
                          #  self.product_infor[product]['buy'].append(acceptablebuy_price)
                        else:
                            acceptablesell_price = acceptablebuy_price
                            acceptablebuy_price = acceptablebuy_price-1
                            
                         #   self.product_infor[product]['sell'].append(acceptablesell_price)
   
           # acceptablebuy_price -= estimate_spread*prefactor
           # acceptablesell_price += estimate_spread*prefactor

            Sumprice = 0
            Sumpricesquare = 0
            totalnum = 0.000000000001 ##prevent (0/0)
            cur_position = state.position.get(product, 0)  
          #  logger.print("Acceptable price : " + str(acceptablebuy_price))

        #   print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
            #Sell_Order, Buy_Order = [], []
            if state.timestamp%timeskip ==0:
                if len(order_depth.sell_orders) != 0:    
                    Sell_Order = sorted(list(order_depth.sell_orders.items()), key=lambda x: x[0]  )
                
                    for ask, amount in Sell_Order: ##amount is negative we want to buy
                        if ask <= acceptablebuy_price: ##buy
                        #    print('kk')
                            if cur_position < position_limit:
                                buyamount = min(position_limit-cur_position,-amount)
                                cur_position += buyamount
                                logger.print("BUY", str(buyamount) + "x", ask)
                                orders.append(Order(product, ask, buyamount)) 
                        Sumprice += ask*(-amount)
                        Sumpricesquare += (ask**2)*(-amount)
                        totalnum += -amount
                        
                if len(order_depth.buy_orders) != 0: ##someone in market want to buy, we want to sell them      
                    Buy_Order = sorted(list(order_depth.buy_orders.items()), key=lambda x: -x[0]  )
        
                    for bid, amount in Buy_Order: ##amount is postive number, we want to sell
                        if bid >= acceptablesell_price: ##sell
                            if cur_position >-position_limit: 
                                sellamount = min(cur_position+position_limit, amount) ## sellamount is a postive number
                                cur_position -= sellamount ## after sell need to subtract it
                                logger.print("SELL", str(sellamount) + "x", bid)
                                orders.append(Order(product, bid, -sellamount))
                        Sumprice += bid*(amount)
                        Sumpricesquare += (bid**2)*amount
                        totalnum += amount    




#                if position_limit >0:
 #                   orders.append(Order(product, round(acceptablesell_price),-cur_position  )) ##sell all 10002
  #              else:
   #                 orders.append(Order(product, round(acceptablebuy_price),  -cur_position)) ##buy all 9998

            Sell_Order = sorted(list(order_depth.sell_orders.items()), key=lambda x: x[0]  )
            Buy_Order = sorted(list(order_depth.buy_orders.items()), key=lambda x: -x[0]  )
                   
            average = Sumprice/totalnum
            averagesquare = Sumpricesquare/totalnum
            Mid_price, Mid_spread = self.midprice_spread(Buy_Order, Sell_Order, True )
            
           # if average!= 0:
            #    self.product_infor[product]['mean'].append(average)
             #   self.product_infor[product]['std'].append((averagesquare-average**2)**0.5)
            if Mid_price != 'No_Mid':
                self.product_infor[product]['mid'].append(Mid_price)
                self.product_infor[product]['spread'].append(Mid_spread)
            
            #if len(self.product_infor[product]['mean'])==self.maxlookback+1:
             #   self.product_infor[product]['mean'].pop(0)
              #  self.product_infor[product]['std'].pop(0)
            if len(self.product_infor[product]['mid'])==self.maxlookback+1:
                self.product_infor[product]['mid'].pop(0)
                self.product_infor[product]['spread'].pop(0)
            

            result[product] = orders
        #print(state.position)
        traderData = jsonpickle.encode(self.product_infor)  

        conversions = 0
        logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData


# In[ ]:




