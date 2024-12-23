import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

class Portfolio:
   """" A class to define a portfolio"""

   def __init__(self, stocks, weights, price_data):
      self.stocks = stocks #list of stocks
      self.weights = weights #list of associated weights
      self.price_data = price_data #dataframe of stock prices (Adj close)

   def get_norm_return(self):
     return self.price_data[self.stocks].pct_change(1)
   
   def get_cum_return(self):
     return self.price_data[self.stocks]/self.price_data[self.stocks].iloc[0]
   
   def compute_markowitz_metrics(self, weights = None):
      log_ret = self.get_norm_return()

      if weights is None :
         weights_arr = np.array(self.weights)
      else:
         weights_arr = np.array(weights) 
   
      port_return =np.sum(log_ret.mean()*weights_arr)*252 # mean annual return
      port_volatility =np.sqrt(np.dot(weights_arr.T,np.dot(log_ret.cov()*252,weights_arr))) # annual volatility
      port_asr = port_return / port_volatility # Sharpe Ratio

      return [port_return, port_volatility, port_asr]
   
   def get_optimal_weights(self, num_ports):
      np.random.seed(101) 

      # Initialisation
      all_weights = np.zeros((num_ports,len(self.weights)))
      ret_arr = np.zeros(num_ports)
      vol_arr = np.zeros(num_ports)
      asr_arr = np.zeros(num_ports)

      for ind in range(num_ports) :
            weights = np.array(np.random.random(len(self.weights)))
            weights = weights/np.sum(weights) # Creation of random weights

            # Saving the weights
            all_weights[ind,:] = weights

            # Compute Markowitz metrics
            result = self.compute_markowitz_metrics(weights)
      
            # Return calculation 
            ret_arr[ind]= result[0]

            # Risk Calculation
            vol_arr[ind] = result[1]

            # Sharpe Ratio
            asr_arr[ind] = result[2]

      print('Done with the Monte Carlo shots. Finding the best allocation ...')

      ind_opti = asr_arr.argmax()
      sharpe_opti = asr_arr[ind_opti]
      print('Highest Sharpe ratio :', round(sharpe_opti,2))
            
      # Expected return with optimal allocation
      ret_opti = ret_arr[ind_opti]
      print('Expected return :', round(100* ret_opti,1), '%')
      # Volatility with optimal allocation
      vol_opti = vol_arr[ind_opti]
      print('Expected volatility :', round(100*vol_opti,1), '%')
      # Optimal allocation
      return all_weights[ind_opti,:]

def plot_correlation(df):
    """" A function to evaluate the matrix correlation of stocks in your portfolio """
    corr = df.corr()

    mask =  np.zeros_like(corr)
    mask[np.triu_indices_from(mask)]=True #triu_indices is used to return the indices for the upper-triangle of an (n,m) array
    with sns.axes_style("white"):
        # color code :
        # - The darker the color, higher is the correlation 
        # - red and its nuances: denotes a negative correlation
        # - yellow and its nuance: denotes a correlation almost null (in general the correlation is really weak in this case)
        # - green and its nuances : a positive correlation
        f,ax  = plt.subplots(figsize=(16,16))
        ax = sns.heatmap(corr, vmin = -1, mask = mask, vmax = 1, cmap='RdYlGn', square = True, annot = True)

def number_stocks_to_allocate(allocated_money, list_stock_price):
   """ a function to determine the stocks to buy or sell depending on the money to allocate and each stock price
      if allocate money is negative, then it's related to a sell order. Otherwise, it's related to a buy order"""
   
   list_num_stocks = []
   for i in range(len(allocated_money)):
      num_stock_in_transit = allocated_money[i] / list_stock_price[i]
      num_stock_in_transit = abs(np.floor(num_stock_in_transit).item())
      list_num_stocks.append(num_stock_in_transit)

   return list_num_stocks

def place_orders(allocated_money, list_stock_price, list_stocks, stock_val_bfr):
   """ a function to place orders according to the money to allocate and determine the value of each stock 
   after placing orders """

   list_num_stocks_orders = []
   stock_val_afr = []
   
   for i,num_stock_in_transit in enumerate(number_stocks_to_allocate(allocated_money, list_stock_price)):
      if num_stock_in_transit == 0:
         list_num_stocks_orders.append(num_stock_in_transit)
         stock_val_afr.append(stock_val_bfr[i])
         print(f"No orders placed for {list_stocks[i]}")
      else:
         if (allocated_money[i] < 0) :
            list_num_stocks_orders.append(-num_stock_in_transit)
            stock_val_afr.append(stock_val_bfr[i]-num_stock_in_transit*list_stock_price[i])
            print(f"Selling {num_stock_in_transit} stocks of {list_stocks[i]}")
         else : 
            list_num_stocks_orders.append(num_stock_in_transit)
            stock_val_afr.append(stock_val_bfr[i]+num_stock_in_transit*list_stock_price[i])
            print(f"Buying {num_stock_in_transit} stocks of {list_stocks[i]}")

   return list_num_stocks_orders , stock_val_afr

def calculate_expenses(num_orders, total_num_stock_in_orders, method = False):
   if method:
      average_fee_per_stock = 0.01 ; # 0.01 dollar
      E = sum([average_fee_per_stock*abs(num) for num in total_num_stock_in_orders])
   else:
      average_fee_per_stock_transaction = 10 ; # 10 dollar
      E = average_fee_per_stock_transaction*len(num_orders) 

   return E