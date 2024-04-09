import numpy as np
import matplotlib.pyplot as plt

def profit (xL, xH):
    return (1/5050) * ((1000-xL)*(xL-900+1)*(xL-900)/2 + (1000-xH)*(xH-xL)*(xH+xL+1-1800)/2)

# price = np.arange(900, 1001, 1)
xL_price = np.arange(945, 955, 1)
xH_price = np.arange(975, 985, 1)
xL_list, xH_list = np.meshgrid(xL_price, xH_price)

plt.imshow(profit(xL_list, xH_list), extent=(xL_price[0]-0.5, xL_price[-1]+0.5, xH_price[0]-0.5, xH_price[-1]+0.5), origin='lower', cmap='jet')
plt.colorbar()
plt.xlabel('xL')
plt.ylabel('xH')
plt.title('Profit')
plt.show()