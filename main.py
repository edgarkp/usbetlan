from src.data_preprocessing import fetch_data , construct_data
from src.utils import plot_correlation, Portfolio
from datetime import date
import pandas as pd
import numpy as np
import os

list_stocks = ['BNP.PA', 'IPS.PA', 'TTE.PA', 'STMPA.PA']
filename = ''
weights_actu  = 25*np.ones(4)
weights_actu = [wt/100 for wt in weights_actu]

for stock in list_stocks:
    filename += stock.split('.')[0] + '_'

filename = filename + date.today().strftime('%Y_%m_%d') 
filepath = 'data/' + filename
#filepath = 'data/BNP_IPS_TTE_STMPA_2024_11_14'

if os.path.exists(filepath) :
    print(f"Loading data from {filepath}")
    df = pd.read_csv(filepath, index_col = 'Date', parse_dates = True)

else: 
    results = fetch_data(list_stocks, '1d')
    df = construct_data(results)

    print(f"Saving data for {filepath}")
    df.to_csv(filepath)

#plot_correlation(df)

portfolio = Portfolio(list_stocks,weights_actu,df)
num_ports = 500 ; # repeating times
print(portfolio.compute_markowitz_metrics())
print(portfolio.weights)
print(portfolio.get_optimal_weights(num_ports))
print(portfolio.weights)