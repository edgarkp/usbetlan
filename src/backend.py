import os
import warnings
warnings.filterwarnings("ignore")

from datetime import date
import yfinance as yf
import pandas as pd
import numpy as np

def fetch_price_data(list_stocks, interval):
    """" A function to read the data from Yahoo Finance """
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

def format_price_data(dict_stock_data):
    """" A function to format the price data fetched in Yahoo Finance """
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

def elt_price_data(list_stocks, interval):
    """" A function performing ELT (Extract Load Transform): 
    to read and format the price data fetched in Yahoo Finance """
    filename = ''
    for stock in list_stocks:
        filename += stock.split('.')[0] + '_'

    filename = filename + date.today().strftime('%Y_%m_%d') 
    filepath = 'data/' + filename
    if os.path.exists(filepath) :
        print(f"Loading data from {filepath}")
        df = pd.read_csv(filepath, index_col = 'Date', parse_dates = True)
    else: 
        results = fetch_price_data(list_stocks, interval)
        df = format_price_data(results)

        print(f"Saving data for {filepath}")
        df.to_csv(filepath)

    return df

def get_previous_portfolio_state() :
    """ A function to retrieve last state (t - 1) of portfolio :
    Vi(t-1) : value of a stock
    wi(t-1) : weight of a stock 
    Vn(t-1) : net portfolio value 
    E(t-1) : Total transactions expenses  
    C(t-1) : Remaining cash from transaction
    
    NB: The available cash in the portfolio is C(t-1) - E(t-1)
    """
    Vo = 100000 # initial investment
    list_value = [25000, 25000, 25000, 25000] 
    Vg = Vo
    Vn = Vo 
    E = 0 
    C = 0 
    list_weights = [0.25, 0.25, 0.25, 0.25]

    results = list_value + [Vg, E, C, Vn]
    print(results)
    return list_weights, results


def update_weights():
    """ A function to check if the Portfolio needs to be updated"""

    return True 

def set_previous_portfolio_state(list_weights, results) :
    """ A function to store the current state t of portfolio :
    Vi(t) : value of a stock
    wi(t) : weight of a stock 
    Vg(t) : gross portfolio value
    Vn(t) : net portfolio value 
    R(t) : portfolio return
    E(t) : Total transactions expenses  
    C(t) : Remaining cash from transaction

    NB: The available cash in the portfolio is C(t) - E(t)"""