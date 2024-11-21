# Import necessary modules
from utils import Portfolio
from data_preprocessing import extract_load_transform_data
import numpy as np


list_stocks = ['BNP.PA', 'IPS.PA', 'TTE.PA', 'STMPA.PA']
Vo = 100000 # initial investment 

# step 1 : Get necessary prices data & previous value of the stock & previous weights 
df = extract_load_transform_data(list_stocks, '1d')
list_price = df.tail(2) # get today and previous day prices

list_value = [25000, 25000, 25000, 25000] # to be in a function such as list_price
Vn_last = Vo # to be in a function such as list_price
E_bfr = 0 # to be in a function such as list_price
C_bfr = 0 # to be in a function such as list_price
list_weights_bfr = [0.25, 0.25, 0.25, 0.25] # to be in function such as list_price
trig_update_weights = True # to be in function such as list_price

portfolio = Portfolio(list_stocks,list_weights_bfr,df) # current portfolio

# step 2 : Calculate the old gross portfolio value Vg(t) before daily weight optimisation
stock_ret_bfr = list_price.pct_change(1).tail(1)
stock_val_bfr = (1 + stock_ret_bfr)*list_value
Vg_bfr = stock_val_bfr.sum(axis = 1).tolist()[0]

# step 3 : Calculate requested weights W(t)
if not(trig_update_weights):
    list_weights = list_weights_bfr
else:
    print("Estimating the optimal weights with current data ...")
    list_weights_opti = portfolio.get_optimal_weights(5000).tolist() 

# step 4: Estimate stock values vi(t) and E(t), expenses and cash after putting orders due to applying new weights
if not(trig_update_weights):
   # do normal computation and store values as in landry portfolio
   results = stock_val_bfr.values.flatten().tolist() # instantiante the data to store
   print(results)
   results.append(Vg_bfr)
   print(results)

   E = 0
   C = 0

   results.append(E)
   results.append(C)

   # step 4 : Calculate the net portfolio value Vn(t)
   Vn = Vg_bfr - E + C 
   results.append(Vn)

   # step 5 : Calculate the yield R(t)
   R = (Vn - Vn_last)/Vn_last
   results.append(R)
   print(results)
else:
    # compute the requested stock values according to newly optimal weights
    stock_val_req = [(Vg_bfr - E_bfr + C_bfr)*w for w in list_weights_opti]
    # compute the number of actions in transaction and each stock realized value
    delta_stock_val = stock_val_req - stock_val_bfr
    delta_stock_val = delta_stock_val.values.flatten().tolist() 
    list_price_today = list_price.values[1].flatten().tolist() 
    stock_val_bfr = stock_val_bfr.values.flatten().tolist() 
    print(delta_stock_val)
    print(list_price_today)

    list_num_stocks = []
    stock_val_afr = []
    
    for i, val in enumerate(delta_stock_val):
        num_stock_in_transit = delta_stock_val[i] / list_price_today[i]
        num_stock_in_transit = np.floor(abs(num_stock_in_transit)).item()

        if num_stock_in_transit == 0:
            list_num_stocks.append(num_stock_in_transit)
            stock_val_afr.append(stock_val_bfr[i])
            print(f"No orders placed for {list_stocks[i]}")
        else:
            if (val < 0) :
                list_num_stocks.append(-num_stock_in_transit)
                stock_val_afr.append(stock_val_bfr[i]-num_stock_in_transit*list_price_today[i])
                print(f"Selling {num_stock_in_transit} stocks on {list_stocks[i]}")
            else : 
                list_num_stocks.append(num_stock_in_transit)
                stock_val_afr.append(stock_val_bfr[i]+num_stock_in_transit*list_price_today[i])
                print(f"Buying {num_stock_in_transit} stocks on {list_stocks[i]}")
    print(list_num_stocks)
    # compute expenses related to the different transactions
    trig_meth_1 = True # consider transaction fee per number of stocks . otherwise, consider fees per transaction

    if trig_meth_1:
        average_fee_per_stock = 0.01 ; # 0.01 dollar
        E = sum([average_fee_per_stock*abs(num) for num in list_num_stocks])
    else:
        average_fee_per_stock_transaction = 10 ; # 10 dollar
        E = average_fee_per_stock_transaction*len(list_stocks) 

# step 5: Calculate realized weights, new gross portfolio & cash value
results = stock_val_afr # instantiante the data to store
print(results)
Vg_afr = sum(stock_val_afr) # new gross portfolio value
list_weights_afr = [val/Vg_afr for val in stock_val_afr] # realized weights
C = Vg_bfr - Vg_afr
results.append(Vg_afr)
results.append(E)
results.append(C)
print(results)

# step 6: Calculate the net portfolio value Vn(t)
Vn = Vg_afr-E+C 
results.append(Vn)

# step 7 : Calculate the yield R(t)
R = (Vn - Vn_last)/Vn_last
results.append(R)

print(results)

print(list_weights_bfr)
print(sum(list_weights_bfr))
print(list_weights_opti)
print(sum(list_weights_opti))
print(list_weights_afr)
print(sum(list_weights_afr))
    
