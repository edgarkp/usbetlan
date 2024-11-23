# Import necessary modules
from utils import Portfolio
from backend import elt_price_data
import numpy as np


list_stocks = ['BNP.PA', 'IPS.PA', 'TTE.PA', 'STMPA.PA']
Vo = 100000 # initial investment 

# step 1 : Get necessary prices data & previous value of the stock 
df = elt_price_data(list_stocks, '1d')
list_price = df.tail(2) # get today and previous day prices

list_value = [25000, 25000, 25000, 25000] # to be in a function such as list_price
list_weights = [0.25, 0.25, 0.25, 0.25] # to be in function such as list_price
Vn_last = Vo # to be in a function such as list_price

# step 2 : Calculate the gross portfolio value Vg(t) 
stock_ret = list_price.pct_change(1).tail(1)
stock_val = (1 + stock_ret)*list_value

Vg = stock_val.sum(axis = 1).tolist()[0]

results = stock_val.values.flatten().tolist() # instantiante the data to store
print(results)
results.append(Vg)
print(results)

# step 3 : Estimate expenses E(t) and cash available C(t)
E = 0
C = 0

results.append(E)
results.append(C)

# step 4 : Calculate the net portfolio value Vn(t)
Vn = Vg - E + C 
results.append(Vn)

# step 5 : Calculate the yield R(t)
R = (Vn - Vn_last)/Vn_last
results.append(R)

print(results)
