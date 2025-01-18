# Import necessary modules
from src.utils import Portfolio, number_stocks_to_allocate, calculate_expenses, place_orders
from src.backend import elt_price_data, get_previous_portfolio_state, set_new_portfolio_state, check_engine

def update_portfolio(PORTFOLIO_ID, TRIG_UPDATE_WEIGHTS,TRIG_METH_EXP,
                     DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DATE):
    # step 0: Connect to the database and fetch previous state
    # PostgreSQL connection string
    DATABASE_URL = f"postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    try:
        engine = check_engine(DATABASE_URL)
        print("Retrieving data ...")
        previous_state = get_previous_portfolio_state(engine, PORTFOLIO_ID, timestamp_current=DATE)
    except Exception as e:
        print(f"Connection failed: {e}")

    # step 1 : Get necessary prices data & previous portfolio state 
    list_stocks, results_bfr = previous_state

    size_list = len(list_stocks)

    list_value = results_bfr[0:size_list]
    list_weights_bfr = results_bfr[size_list:2*size_list]
    Vg_last = results_bfr[2*size_list]
    E_bfr = results_bfr[2*size_list+1] 
    C_bfr = results_bfr[2*size_list+2] 
    Vn_last = results_bfr[2*size_list+3] 

    df = elt_price_data(list_stocks, interval = '1d', timestamp = DATE)

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
        delta_stock_val_req = stock_val_req - stock_val_bfr

        delta_stock_val_req = delta_stock_val_req.values.flatten().tolist() 
        list_price_today = list_price.values[1].flatten().tolist() 
  
        list_num_stocks_req = number_stocks_to_allocate(delta_stock_val_req, list_price_today)
        E_req = calculate_expenses(list_stocks, list_num_stocks_req, TRIG_METH_EXP) # anticipated expenses
        
        # 4b - compute the realized transactions
        stock_val_realized = [(Vg_bfr - E_bfr + C_bfr - E_req)*w for w in list_weights_opti]
        delta_stock_val_realized = stock_val_realized - stock_val_bfr
        delta_stock_val_realized = delta_stock_val_realized.values.flatten().tolist()
        stock_val_bfr = stock_val_bfr.values.flatten().tolist() 

        list_num_stocks_orders , stock_val_afr = place_orders(delta_stock_val_realized, list_price_today, list_stocks, stock_val_bfr)
        
        # 4c - compute e
        # xpenses related to the different realized transactions
        E = calculate_expenses(list_stocks, list_num_stocks_orders, TRIG_METH_EXP)

        # 4d - calculate realized weights, new gross portfolio & cash value
        results_afr = [] # instantiante the data to store
        list_weights_afr = []

        results_afr = stock_val_afr 

        Vg_afr = sum(stock_val_afr) # new gross portfolio value
        list_weights_afr = [val/Vg_afr for val in stock_val_afr]
        
        results_afr.extend(list_weights_afr)

        C = Vg_bfr - E_bfr + C_bfr - Vg_afr # cash left from transaction : what i try to allocate vs what i allocated
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
    set_new_portfolio_state(engine, PORTFOLIO_ID, list_stocks, results_afr, timestamp = DATE)
    print("Storing complete")

