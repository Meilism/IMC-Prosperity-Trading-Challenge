import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json


__all__ = ["log_file_analyzer"]

class log_file_analyzer:
    def __init__(self, product_list: list[str], logfilename: str):
        self.product_list = product_list
        self.read_log_file(logfilename)

    def read_log_file(self, logfilename: str):
        with open(logfilename, 'r') as logfile:
            for line_num, line_content in enumerate(logfile):
                if "Sandbox logs:" in line_content:
                    sandbox_log_start = line_num
                    # print(f"Found 'Sandbox logs:' at line {line_num}")

                if "Activities log:" in line_content:
                    activities_log_start = line_num
                    # print(f"Found 'Activities log:' at line {line_num}")
                    
                if "Trade History:" in line_content:
                    trade_history_start = line_num
                    # print(f"Found 'Trade History:' at line {line_num}")

            logfile.seek(0) # reset reading position to the beginning of the file
            trade_history_lines = logfile.readlines()[trade_history_start+1:]
            self.trade_history_log = json.loads('\n'.join(trade_history_lines))

        self.df_activity_log = pd.read_csv(logfilename, skiprows=activities_log_start+1, 
                                            nrows=trade_history_start-activities_log_start-6, # 4000 lines
                                            skip_blank_lines=False, sep=';')
        
    def analyze_product_prices(self, product: str) -> tuple[np.ndarray]:

        assert product in self.product_list, f"Product {product} not found."

        product_rows = self.df_activity_log["product"] == product

        timestamp = self.df_activity_log["timestamp"][product_rows]

        bid_price_1 = self.df_activity_log["bid_price_1"][product_rows]
        bid_price_2 = self.df_activity_log["bid_price_2"][product_rows]
        bid_price_3 = self.df_activity_log["bid_price_3"][product_rows]
        bid_volume_1 = self.df_activity_log["bid_volume_1"][product_rows]
        bid_volume_2 = self.df_activity_log["bid_volume_2"][product_rows]
        bid_volume_3 = self.df_activity_log["bid_volume_3"][product_rows]

        bid_prices = np.vstack((bid_price_1.fillna(0).to_numpy(), 
                                bid_price_2.fillna(0).to_numpy(), 
                                bid_price_3.fillna(0).to_numpy()))
        bid_volumes = np.vstack((bid_volume_1.fillna(0).to_numpy(),
                                bid_volume_2.fillna(0).to_numpy(),
                                bid_volume_3.fillna(0).to_numpy()))
        
        bid_price_ave = np.average(bid_prices, axis=0, weights=bid_volumes)
        bid_price_var = np.average((bid_prices-bid_price_ave)**2, axis=0, weights=bid_volumes)
        bid_price_std = np.sqrt(bid_price_var)

        ask_price_1 = self.df_activity_log["ask_price_1"][product_rows]
        ask_price_2 = self.df_activity_log["ask_price_2"][product_rows]
        ask_price_3 = self.df_activity_log["ask_price_3"][product_rows]
        ask_volume_1 = self.df_activity_log["ask_volume_1"][product_rows]
        ask_volume_2 = self.df_activity_log["ask_volume_2"][product_rows]
        ask_volume_3 = self.df_activity_log["ask_volume_3"][product_rows]

        ask_prices = np.vstack((ask_price_1.fillna(0).to_numpy(),
                                ask_price_2.fillna(0).to_numpy(),
                                ask_price_3.fillna(0).to_numpy()))
        ask_volumes = np.vstack((ask_volume_1.fillna(0).to_numpy(),
                                ask_volume_2.fillna(0).to_numpy(),
                                ask_volume_3.fillna(0).to_numpy()))
        
        ask_price_ave = np.average(ask_prices, axis=0, weights=ask_volumes)
        ask_price_var = np.average((ask_prices-ask_price_ave)**2, axis=0, weights=ask_volumes)
        ask_price_std = np.sqrt(ask_price_var)

        return timestamp, bid_price_ave, bid_price_std, ask_price_ave, ask_price_std
    
    def plot_product_prices(self, product: str, save_fig: bool = False, save_name: str = None) -> None:

        timestamp, bid_price_ave, bid_price_std, ask_price_ave, ask_price_std = self.analyze_product_prices(product)
    
        plt.figure(figsize=(15, 5))
        plt.errorbar(timestamp, bid_price_ave, yerr=bid_price_std, fmt='o', markersize=2, elinewidth=.4, label='ave_bid_price')
        plt.errorbar(timestamp, ask_price_ave, yerr=ask_price_std, fmt='o', markersize=2, elinewidth=.4, label='ave_ask_price')
        plt.xlabel("Timestamp")
        plt.ylabel("Price")
        plt.title(f"{product} prices")
        plt.legend()
        plt.grid()
        plt.tight_layout()

        if save_fig:
            if save_name is None:
                plt.savefig(f"{product}_prices.png", dpi=300)
            else:
                plt.savefig(save_name, dpi=300)

    def analyze_profit(self, product: str) -> tuple[np.ndarray]:

        assert product in self.product_list, f"Product {product} not found."

        product_rows = self.df_activity_log["product"] == product
        timestamp = self.df_activity_log["timestamp"][product_rows]
        profit = self.df_activity_log["profit_and_loss"][product_rows]

        return timestamp, profit
    
    def plot_profit_and_loss(self, save_fig: bool = False, save_name: str = None) -> None:

        plt.figure(figsize=(15, 5))
        for product in self.product_list:
            timestamp, profit = self.analyze_profit(product)
            plt.plot(timestamp, profit, 'o', markersize=2, label=f"{product}_profit")
        plt.xlabel("Timestamp")
        plt.title("Profit and loss")
        plt.legend()
        plt.grid()
        plt.tight_layout()

        if save_fig:
            if save_name is None:
                plt.savefig("profit.png", dpi=300)
            else:
                plt.savefig(save_name, dpi=300)
        
    def analyze_trade_history(self, product: str) -> tuple[np.ndarray]:
            
        assert product in self.product_list, f"Product {product} not found."

        market_trades = {}
        my_bid_trades = {}
        my_sell_trades = {}
        for trade in self.trade_history_log:
            if trade["symbol"] != product:
                continue

            if trade["buyer"] == "SUBMISSION":
                if trade["timestamp"] not in my_bid_trades.keys():
                    my_bid_trades[trade["timestamp"]] = {"price": [], "quantity": []}
                my_bid_trades[trade["timestamp"]]["price"].append(trade["price"])
                my_bid_trades[trade["timestamp"]]["quantity"].append(trade["quantity"])
            elif trade["seller"] == "SUBMISSION":
                if trade["timestamp"] not in my_sell_trades.keys():
                    my_sell_trades[trade["timestamp"]] = {"price": [], "quantity": []}
                my_sell_trades[trade["timestamp"]]["price"].append(trade["price"])
                my_sell_trades[trade["timestamp"]]["quantity"].append(trade["quantity"])
            else:
                if trade["timestamp"] not in market_trades.keys():
                    market_trades[trade["timestamp"]] = {"price": [], "quantity": []}
                market_trades[trade["timestamp"]]["price"].append(trade["price"])
                market_trades[trade["timestamp"]]["quantity"].append(trade["quantity"])
        
        market_trades_timestamp = np.empty(len(market_trades.keys()))
        market_price_ave = np.empty(len(market_trades.keys()))
        market_price_std = np.empty(len(market_trades.keys()))
        for i, (timestamp, trade) in enumerate(market_trades.items()):
            market_trades_timestamp[i] = timestamp
            price = np.array(trade["price"])
            quantity = np.array(trade["quantity"])
            ave = np.average(price, weights=quantity)
            var = np.average((price-ave)**2, weights=quantity)
            std = np.sqrt(var)
            market_price_ave[i] = ave
            market_price_std[i] = std

        my_bid_trades_timestamp = np.empty(len(my_bid_trades.keys()))
        my_bid_price_ave = np.empty(len(my_bid_trades.keys()))
        my_bid_price_std = np.empty(len(my_bid_trades.keys()))
        for i, (timestamp, trade) in enumerate(my_bid_trades.items()):
            my_bid_trades_timestamp[i] = timestamp
            price = np.array(trade["price"])
            quantity = np.array(trade["quantity"])
            ave = np.average(price, weights=quantity)
            var = np.average((price-ave)**2, weights=quantity)
            std = np.sqrt(var)
            my_bid_price_ave[i] = ave
            my_bid_price_std[i] = std

        my_sell_trades_timestamp = np.empty(len(my_sell_trades.keys()))
        my_sell_price_ave = np.empty(len(my_sell_trades.keys()))
        my_sell_price_std = np.empty(len(my_sell_trades.keys()))
        for i, (timestamp, trade) in enumerate(my_sell_trades.items()):
            my_sell_trades_timestamp[i] = timestamp
            price = np.array(trade["price"])
            quantity = np.array(trade["quantity"])
            ave = np.average(price, weights=quantity)
            var = np.average((price-ave)**2, weights=quantity)
            std = np.sqrt(var)
            my_sell_price_ave[i] = ave
            my_sell_price_std[i] = std

        return (market_trades_timestamp, market_price_ave, market_price_std, 
                my_bid_trades_timestamp, my_bid_price_ave, my_bid_price_std, 
                my_sell_trades_timestamp, my_sell_price_ave, my_sell_price_std)
    
    def plot_trade_history(self, product: str, save_fig: bool = False, save_name: str = None) -> None:
            
        (market_trades_timestamp, market_price_ave, market_price_std, 
        my_bid_trades_timestamp, my_bid_price_ave, my_bid_price_std, 
        my_sell_trades_timestamp, my_sell_price_ave, my_sell_price_std) = self.analyze_trade_history(product)
        
        plt.figure(figsize=(15, 5))
        plt.errorbar(my_bid_trades_timestamp, my_bid_price_ave, yerr=my_bid_price_std, fmt='o', markersize=5, elinewidth=.4, label='my_bid_trades')
        plt.errorbar(my_sell_trades_timestamp, my_sell_price_ave, yerr=my_sell_price_std, fmt='o', markersize=5, elinewidth=1, label='my_sell_trades')
        plt.errorbar(market_trades_timestamp, market_price_ave, yerr=market_price_std, fmt='o', markersize=2, elinewidth=.4, label='market_trades')
        plt.xlabel("Timestamp")
        plt.ylabel("Price")
        plt.title(f"{product} trade history")
        plt.legend()
        plt.grid()
        plt.tight_layout()

        if save_fig:
            if save_name is None:
                plt.savefig(f"{product}_trade_history.png", dpi=300)
            else:
                plt.savefig(save_name, dpi=300)
