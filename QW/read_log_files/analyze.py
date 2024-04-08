import matplotlib.pyplot as plt
import numpy as np

from log_file_analyzer import log_file_analyzer

product_list = ["AMETHYSTS", "STARFRUIT"]
round_num = 'tutorial'
trader_num = 3
logfilename = f'codes/round_{round_num}/trader_{trader_num}/log_trader_{trader_num}.log'
analyze = log_file_analyzer(product_list, logfilename)

analyze.plot_product_prices("STARFRUIT", save_fig=False, save_name="codes/round_tutorial/STARFRUIT_prices.png")
analyze.plot_product_prices("AMETHYSTS", save_fig=False, save_name="codes/round_tutorial/AMETHYSTS_prices.png")
analyze.plot_profit_and_loss(save_fig=True, save_name=f"codes/round_{round_num}/trader_{trader_num}/profit_trader_{trader_num}.png")
analyze.plot_trade_history("STARFRUIT", save_fig=True, save_name=f"codes/round_{round_num}/trader_{trader_num}/STARFRUIT_trade_history_trader_{trader_num}.png")
analyze.plot_trade_history("AMETHYSTS", save_fig=True, save_name=f"codes/round_{round_num}/trader_{trader_num}/AMETHYSTS_trade_history_trader_{trader_num}.png")

plt.show()