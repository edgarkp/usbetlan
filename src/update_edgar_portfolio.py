# Import necessary modules
from utils import Portfolio
from backend import elt_price_data, get_previous_portfolio_state, set_new_portfolio_state, check_engine
import numpy as np

# inputs to my main function
portfolio_id = 1
trig_update_weights = True

# step 0: Connect to the database and fetch previous state
# Connection info
username = "postgres"
password = "myfirstdatabase"
host = "portfoliodb.cxcciogmujrs.eu-north-1.rds.amazonaws.com"
port = "5432"
database = "initial_db"

# PostgreSQL connection string
DATABASE_URL = f"postgresql+psycopg://{username}:{password}@{host}:{port}/{database}"

try:
    engine = check_engine(DATABASE_URL)
    print("Retrieving data ...")
    previous_state = get_previous_portfolio_state(engine, portfolio_id)

except Exception as e:
    print(f"Connection failed: {e}")

# step 1 : Get necessary prices data & previous value of the stock & previous weights 
list_stocks, results = previous_state

list_value = results[0:4]
list_weights_bfr = results[4:8]
Vg_last = results[8]
E_bfr = results[9] 
C_bfr = results[10] 
Vn_last = results[11] 
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
if not(trig_update_weights):
    print('No weights update')
    list_weights_afr = list_weights_bfr
else:
    print("Estimating the optimal weights with current data ...")
    list_weights_opti = portfolio.get_optimal_weights(5000).tolist() 

# step 4: Estimate stock values vi(t) and E(t), expenses and cash after putting orders due to applying new weights
if not(trig_update_weights):
   # do normal computation and store values as in landry portfolio
   results = stock_val_bfr.values.flatten().tolist() # instantiante the data to store
   results.append(Vg_bfr)

   E = 0
   C = 0
   results.append(E)
   results.append(C)

   # Calculate the net portfolio value Vn(t)
   Vn = Vg_bfr - E + C 
   results.append(Vn)

   # Calculate the yield R(t)
   R = (Vn - Vn_last)/Vn_last
   results.append(R)
   
else:
    print(f"Reallocating {round(Vg_bfr - E_bfr + C_bfr)} with the requested weights :")
    for i,w in enumerate(list_weights_opti):
        print(f"{list_stocks[i]} : {round(w*100)}% ")
    
    # compute the requested stock values according to newly optimal weights
    stock_val_req = [(Vg_bfr - E_bfr + C_bfr)*w for w in list_weights_opti]
    # compute the number of actions in transaction and each stock realized value
    delta_stock_val = stock_val_req - stock_val_bfr
    delta_stock_val = delta_stock_val.values.flatten().tolist() 
    list_price_today = list_price.values[1].flatten().tolist() 
    stock_val_bfr = stock_val_bfr.values.flatten().tolist() 
    print(sum(delta_stock_val))
    print(list_price_today)

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

    # compute expenses related to the different transactions
    trig_meth_1 = True # consider transaction fee per number of stocks . otherwise, consider fees per transaction

    if trig_meth_1:
        average_fee_per_stock = 0.01 ; # 0.01 dollar
        E = sum([average_fee_per_stock*abs(num) for num in list_num_stocks])
    else:
        average_fee_per_stock_transaction = 10 ; # 10 dollar
        E = average_fee_per_stock_transaction*len(list_stocks) 

    # step 5: Calculate realized weights, new gross portfolio & cash value
    results = [] # instantiante the data to store
    list_weights_afr = []

    results = stock_val_afr 

    Vg_afr = sum(stock_val_afr) # new gross portfolio value
    for val in stock_val_afr :# realized weights
        w = val/Vg_afr
        results.append(w)
       # list_weights_afr.append(w)
    
    C = Vg_bfr - Vg_afr # cash left from transaction
    results.append(Vg_afr)
    results.append(E)
    results.append(C)

    # step 6: Calculate the net portfolio value Vn(t)
    Vn = Vg_afr-E+C 
    results.append(Vn)

    # step 7 : Calculate the yield R(t)
    R = (Vn - Vn_last)/Vn_last
    results.append(R)

    print(f"Current state of your portfolio after allocation : \
        {'\n'}    Gross portfolio value: {round(Vg_afr)} \
        {'\n'}    Available Cash : {round(C - E)} \
        {'\n'}    Net portfolio value: {round(Vn)}")
    
    print(f"Allocation evolution (previous -> requested -> current): ")
    for i,w in enumerate(list_weights_opti):
            print(f"{list_stocks[i]} : {round(list_weights_bfr[i]*100)}% -> {round(w*100)}% -> {round(list_weights_afr[i]*100)}%")

# step 8 : Save results
print("Storing data ...")
set_new_portfolio_state(engine, portfolio_id, list_stocks, results)
print("Storing complete")
    

    
