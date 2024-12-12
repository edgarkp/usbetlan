from backend import get_previous_portfolio_state, set_new_portfolio_state, get_table_name_by_id,check_engine
import os

# Connection info
DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ['DB_NAME']

# PostgreSQL connection string
DATABASE_URL = f"postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    engine = check_engine(DATABASE_URL)

    print("Retrieving data ...")
    latest_state = get_previous_portfolio_state(engine, 1)
    print('Latest portfolio state: ', latest_state)

    # list_stocks = ['BNP.PA', 'IPS.PA', 'TTE.PA', 'STMPA.PA']
    # list_weights_afr = [0.25, 0.25, 0.25, 0.25]
    # results = [25000, 25000, 25000, 25000, 0.25, 0.25, 0.25, 0.25, 100000, 0, 0, 100000,  0]
    # id = 4
    # # for id in range(1,4):
    # set_new_portfolio_state(engine, id, list_stocks, results)
        
except Exception as e:
    print(f"Connection failed: {e}")
