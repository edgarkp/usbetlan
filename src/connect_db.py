from backend import get_previous_portfolio_state, set_previous_portfolio_state
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Table, Column, MetaData, JSON, Float, TIMESTAMP

# Connection info
username = "postgres"
password = "myfirstdatabase"
host = "portfoliodb.cxcciogmujrs.eu-north-1.rds.amazonaws.com"
port = "5432"
database = "initial_db"

# PostgreSQL connection string
DATABASE_URL = f"postgresql+psycopg://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("Connection successful!")

        metadata = MetaData()
        
    # Define tables
    portfolio_states = Table (
        "portfolio_states", metadata,
        Column("timestamp", TIMESTAMP, primary_key = True),
        Column("stocks", JSON, nullable = False),
        Column("gross_portfolio_value", Float, nullable = True),
        Column("total_transaction_fees", Float, nullable= True),
        Column("available_cash", Float, nullable= True),
        Column("net_portfolio_value", Float, nullable = True),
        Column("portfolio_return", Float, nullable = True)
    )

    portfolio_weights = Table (
        "portfolio_weights", metadata,
        Column("timestamp", TIMESTAMP, primary_key = True),
        Column("weights", JSON, nullable = False)
    )
    
    metadata.create_all(engine)

    with Session(engine) as session:
        # print("Retrieving data ...")
        # latest_state = get_previous_portfolio_state(session, portfolio_states, portfolio_weights)
        # print('Latest portfolio state: ', latest_state)
        list_stocks = ['BNP.PA', 'IPS.PA', 'TTE.PA', 'STMPA.PA']
        list_weights_afr = [0.6303739856886065, 0.07167028556244925, 0.2952216194100796, 0.002734109338864649]
        results = [63739.24366420825, 7246.824740012278, 29850.85546315133, 276.455033537135, 101113.37890090898, 21.56, 144.92068099975586, 101236.73958190874,  0.012367395819087397]
        set_previous_portfolio_state(session, portfolio_states, portfolio_weights, list_stocks, list_weights_afr, results)
        


except Exception as e:
    print(f"Connection failed: {e}")
