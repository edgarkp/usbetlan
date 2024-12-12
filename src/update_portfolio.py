# Import necessary modules
from utils import Portfolio
from backend import elt_price_data, get_previous_portfolio_state, set_new_portfolio_state, check_engine
import numpy as np
import os

# inputs to my main function
PORTFOLIO_ID = 4
TRIG_UPDATE_WEIGHTS = False
TRIG_METH_EXP = True # consider transaction fee per number of stocks . otherwise, consider fees per transaction

# Connection info
DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']

# step 0: Connect to the database and fetch previous state
# PostgreSQL connection string
DATABASE_URL = f"postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    engine = check_engine(DATABASE_URL)
    print("Retrieving data ...")
    previous_state = get_previous_portfolio_state(engine, PORTFOLIO_ID)
except Exception as e:
    print(f"Connection failed: {e}")

# step 1 : Get necessary prices data & previous portfolio state 
list_stocks, results_bfr = previous_state

list_value = results_bfr[0:4]
list_weights_bfr = results_bfr[4:8]
Vg_last = results_bfr[8]
E_bfr = results_bfr[9] 
C_bfr = results_bfr[10] 
Vn_last = results_bfr[11] 
df = elt_price_data(list_stocks, '1d')

portfolio = Portfolio(list_stocks,list_weights_bfr,df) # current portfolio

print(f"Previous state of your portfolio : \
      {'\n'}    Gross portfolio value: {round(Vg_last)}\
      {'\n'}    Available Cash : {round(C_bfr - E_bfr)} \
      {'\n'}    Net portfolio value: {round(Vn_last)}")

# step 2 : Calculate the old gross portfolio value Vg(t) before daily weight optimisation
list_price = df.tail(2) # get today and previous day prices
stock_ret_bfr = list_price.pct_change(1).tail(1)
stock_val_bfr = (1 + stock_ret_bfr)*list_value
Vg_bfr = stock_val_bfr.sum(axis = 1).tolist()[0]
print(f"Current state of your portfolio before allocation : \
      {'\n'}    Gross portfolio value: {round(Vg_bfr)} \
      {'\n'}    Available Cash : {round(C_bfr - E_bfr)} \
      {'\n'}    Net portfolio value: {round(Vg_bfr - E_bfr + C_bfr)}")

delta_Vg_bfr = round(Vg_bfr - Vg_last)

if (delta_Vg_bfr) < 0 :
    print(f"Your gross portfolio value has decreased by {abs(delta_Vg_bfr)}")
elif (delta_Vg_bfr) > 0 :
    print(f"Your gross portfolio value has raised by {abs(delta_Vg_bfr)}")
else:
    print(f"No change in gross portfolio value")

# step 3 : Calculate requested weights W(t)
if not(TRIG_UPDATE_WEIGHTS):
    print('No weights update')
    list_weights_afr = list_weights_bfr
else:
    print("Estimating the optimal weights with current data ...")
    list_weights_opti = portfolio.get_optimal_weights(5000).tolist() 

# step 4: Estimate stock values, expenses, available cash, net & gross portfolio value & portfolio return 
if not(TRIG_UPDATE_WEIGHTS):
   # do normal computation and store values
   results_afr = stock_val_bfr.values.flatten().tolist() # instantiante the data to store
   results_afr.extend(list_weights_afr)
   results_afr.append(Vg_bfr)

   E = 0
   C = 0
   results_afr.append(E)
   results_afr.append(C)

   # Calculate the net portfolio value Vn(t)
   Vn = Vg_bfr - E + C 
   results_afr.append(Vn)

   # Calculate the yield R(t)
   R = (Vn - Vn_last)/Vn_last
   results_afr.append(R)
   
else:
    print(f"Reallocating {round(Vg_bfr - E_bfr + C_bfr)} with the requested weights :")
    for i,w in enumerate(list_weights_opti):
        print(f"{list_stocks[i]} : {round(w*100)}% ")
    
    # 4a - compute the requested stock values according to newly optimal weights
    stock_val_req = [(Vg_bfr - E_bfr + C_bfr)*w for w in list_weights_opti]
    # 4b - compute the number of actions in transaction and each stock realized value
    delta_stock_val = stock_val_req - stock_val_bfr
    delta_stock_val = delta_stock_val.values.flatten().tolist() 
    list_price_today = list_price.values[1].flatten().tolist() 
    stock_val_bfr = stock_val_bfr.values.flatten().tolist() 

    list_num_stocks = []
    stock_val_afr = []
    
    for i, val in enumerate(delta_stock_val):
        num_stock_in_transit = delta_stock_val[i] / list_price_today[i]
        num_stock_in_transit = abs(np.floor(num_stock_in_transit).item())

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

    # 4c - compute expenses related to the different transactions
    if TRIG_METH_EXP:
        average_fee_per_stock = 0.01 ; # 0.01 dollar
        E = sum([average_fee_per_stock*abs(num) for num in list_num_stocks])
    else:
        average_fee_per_stock_transaction = 10 ; # 10 dollar
        E = average_fee_per_stock_transaction*len(list_stocks) 

    # 4d - calculate realized weights, new gross portfolio & cash value
    results_afr = [] # instantiante the data to store
    list_weights_afr = []

    results_afr = stock_val_afr 

    Vg_afr = sum(stock_val_afr) # new gross portfolio value
    list_weights_afr = [val/Vg_afr for val in stock_val_afr]
    
    results_afr.extend(list_weights_afr)

    C = Vg_bfr - Vg_afr # cash left from transaction
    results_afr.append(Vg_afr)
    results_afr.append(E)
    results_afr.append(C)

    # 4e - calculate the net portfolio value Vn(t)
    Vn = Vg_afr-E+C 
    results_afr.append(Vn)

    # 4f - calculate the yield R(t)
    R = (Vn - Vn_last)/Vn_last
    results_afr.append(R)

    print(f"Current state of your portfolio after allocation : \
        {'\n'}    Gross portfolio value: {round(Vg_afr)} \
        {'\n'}    Available Cash : {round(C - E)} \
        {'\n'}    Net portfolio value: {round(Vn)}")
    
    print(f"Allocation evolution (previous -> requested -> current): ")
    for i,w in enumerate(list_weights_opti):
            print(f"{list_stocks[i]} : {round(list_weights_bfr[i]*100)}% -> {round(w*100)}% -> {round(list_weights_afr[i]*100)}%")


# step 5 : Save results
print("Storing new portfolio state ...")
set_new_portfolio_state(engine, PORTFOLIO_ID, list_stocks, results_afr)
print("Storing complete")
    

    
