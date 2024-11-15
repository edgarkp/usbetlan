# This set of functions are used to fetch values in YF database and construct inputs for Optimization
import pandas as pd
import numpy as np
from datetime import date
import yfinance as yf

import warnings
warnings.filterwarnings("ignore")

def fetch_data(list_stocks, interval):

    dict_stock_data = dict()

    today = date.today()
    for stock in list_stocks:
        #ticker = yf.Ticker(stock)
        if interval == '1d' :
            stock_data = yf.download(stock, interval='1d')    
        else : # preferably intraday data (ex: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h)
            stock_data = yf.download(stock, start = today, end = None, interval= interval)

        dict_stock_data[stock] = stock_data

    return dict_stock_data

def construct_data(dict_stock_data):
    duration = 660 #30 months of recording data
    length=[]

    for (symbol, stock_df) in dict_stock_data.items():
        length.append(len(stock_df))

    if any(l < duration for l in length):
        ind_l =  np.array(length).argmin() # check the shortest dataframe
        duration = length[ind_l] # update the window duration
        test_stock_df = list(dict_stock_data.values())[ind_l] #get its content
        start = test_stock_df.index[0]
        end = test_stock_df.index[-1]
    else :
        # Get the study window from a test symbol
        test_stock_df = list(dict_stock_data.values())[0]
        s = len(test_stock_df.index) 
        start = test_stock_df.index[s-duration]
        end = test_stock_df.index[-1]

    # Initialize table
    timestamp_indices = test_stock_df[start:end].index #Extract indices
    list_symbols = list(dict_stock_data.keys())
    df = pd.DataFrame(0,index = timestamp_indices,columns = list_symbols)

    # Assign values of normalized return inside that table
    for symbol in dict_stock_data.keys() :
        selected_stock_data = dict_stock_data[symbol]
        stock_df = selected_stock_data[start:end]
        df[symbol]=stock_df['Adj Close']

    return df