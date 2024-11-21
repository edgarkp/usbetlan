from src.data_preprocessing import extract_load_transform_data
from src.utils import plot_correlation, Portfolio
from datetime import date
import pandas as pd
import numpy as np
import os

list_stocks = ['BNP.PA', 'IPS.PA', 'TTE.PA', 'STMPA.PA']
weights_actu  = 25*np.ones(4)
weights_actu = [wt/100 for wt in weights_actu]

df = extract_load_transform_data(list_stocks, '1d')

#plot_correlation(df)

portfolio = Portfolio(list_stocks,weights_actu,df)
num_ports = 500 ; # repeating times
print(portfolio.compute_markowitz_metrics())
print(portfolio.weights)
print(portfolio.get_optimal_weights(num_ports))
print(portfolio.weights)