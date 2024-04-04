#!/usr/bin/env python
# coding: utf-8

# In[208]:


from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import jsonpickle

class Trader:
    
    def run(self,state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        
        if state.traderData == "":
            productaverage={}
				# Orders to be placed on exchange matching engine
        else:
            productaverage = jsonpickle.decode(state.traderData)
        result = {}
    
        
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
                
            
            if product not in productaverage:
                productaverage[product] =[]
            if len(productaverage[product]) == 0:
                acceptable_price = 0
            else:
                acceptable_price = sum(productaverage[product])/len(productaverage[product])
            
            Sumprice = 0
            totalnum = 0
            
        
            
            print("Acceptable price : " + str(acceptable_price))
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                
                if int(best_ask) < acceptable_price:
                    if best_ask_amount <-20:
                        best_ask_amount = -20
                    print("BUY", str(-best_ask_amount) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_amount))
             #   print(order_depth.sell_orders,'**')
                for price, numb in order_depth.sell_orders.items():
                    Sumprice += price*(-numb)
                    totalnum += -numb
        
    
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                print(list(order_depth.buy_orders.items())[0])
                if int(best_bid) > acceptable_price:
                    if best_bid_amount > 20:
                        best_bid_amount = 20
                    print("SELL", str(best_bid_amount) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_amount))
                
                for price, numb in order_depth.buy_orders.items():
                    Sumprice += price*(numb)
                    totalnum += numb
                    
            productaverage[product].append(Sumprice/totalnum)
            if len(productaverage[product])==21:
                productaverage[product].pop(0)
            
            result[product] = orders
      #  print(productaverage,'******')
		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        
        traderData = jsonpickle.encode(productaverage)  
        #state.traderData = traderData
        #traderData = state.traderData
        print('******'+traderData+'********')
				# Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, traderData


# In[ ]:





# In[206]:


#trader1 = Trader
#Trader.run(trader1,state)


# In[ ]:




