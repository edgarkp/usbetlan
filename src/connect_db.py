from backend import get_previous_portfolio_state, set_new_portfolio_state, get_table_name_by_id,check_engine

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

    # print("Retrieving data ...")
    # latest_state = get_previous_portfolio_state(engine, 1)
    # print('Latest portfolio state: ', latest_state)

    list_stocks = ['BNP.PA', 'IPS.PA', 'TTE.PA', 'STMPA.PA']
    list_weights_afr = [0.25, 0.25, 0.25, 0.25]
    results = [25000, 25000, 25000, 25000, 0.25, 0.25, 0.25, 0.25, 100000, 0, 0, 100000,  0]
    id = 4
    # for id in range(1,4):
    set_new_portfolio_state(engine, id, list_stocks, results)
        
except Exception as e:
    print(f"Connection failed: {e}")
