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

# class PortfolioState(Portfolio):
#    """" A class to define the portfolio status"""

#    def __init__(self, stock_value, gross_value, transaction_fees, gross_cash, net_value, return_port) :
#         self.stock_value = stock_value 
#         self.gross_value = gross_value 
#         self.transaction_fees = transaction_fees 
#         self.gross_cash = gross_cash 
#         self.net_value = net_value 
#         self.return_port = return_port 

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