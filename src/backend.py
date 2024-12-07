import os
import warnings
warnings.filterwarnings("ignore")

from datetime import date, datetime
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

def get_previous_portfolio_state(session, portfolio_states, portfolio_weights) :
    """ A function to retrieve last state (t - 1) of portfolio :
    Vi(t-1) : value of a stock
    wi(t-1) : weight of a stock 
    Vn(t-1) : net portfolio value 
    E(t-1) : Total transactions expenses  
    C(t-1) : Remaining cash from transaction
    
    NB: The available cash in the portfolio is C(t-1) - E(t-1)
    """
    query_states = portfolio_states.select().order_by(portfolio_states.c.timestamp.desc()).limit(1)
    query_weights = portfolio_weights.select().order_by(portfolio_weights.c.timestamp.desc()).limit(1)
    
    data_states = session.execute(query_states).fetchone()
    data_weights = session.execute(query_weights).fetchone()

    (timestamp_states, list_value_raw, Vg, E, C, Vn, R) = data_states
    (timestamp_weights, list_weights_raw) = data_weights

    if timestamp_weights == timestamp_states :
       list_stocks = [i for i in list_value_raw.keys()]
       list_weights = [val for val in list_weights_raw.values()]
       results = [val for val in list_value_raw.values()]
       results.append(Vg)
       results.append(E)
       results.append(C)
       results.append(Vn)
       results.append(R)
       
       return list_stocks, list_weights, results
    else:
        print("the extracted timestamps don't match")

def update_weights():
    """ A function to check if the Portfolio needs to be updated"""

    return True 

def set_previous_portfolio_state(session, portfolio_states, portfolio_weights, list_stocks, list_weights, results) :
    """ A function to store the current state t of portfolio :
    Vi(t) : value of a stock
    wi(t) : weight of a stock 
    Vg(t) : gross portfolio value
    Vn(t) : net portfolio value 
    R(t) : portfolio return
    E(t) : Total transactions expenses  
    C(t) : Remaining cash from transaction

    NB: The available cash in the portfolio is C(t) - E(t)"""
    timestamp = datetime.now().strftime('%Y-%b-%d')

    list_value = results[0:3]

    dict_vals = dict()
    dict_weights = dict()

    for i in range(len(list_stocks)-1):
        stock = list_stocks[i]
        val = list_value[i]
        weight = list_weights[i]

        dict_vals[stock] = val
        dict_weights[stock] = weight

    current_state = {
        "timestamp": timestamp,
        "stocks": dict_vals,
        "gross_portfolio_value": results[4],
        "total_transaction_fees": results[5],
        "available_cash": results[6],
        "net_portfolio_value": results[7],
        "portfolio_return": results[8] 
    }

    current_weight = {
        "timestamp": timestamp,
        "weights": dict_weights,
    }

    session.execute(portfolio_states.insert().values(current_state))
    session.execute(portfolio_weights.insert().values(current_weight))
    session.commit()

