# Import necessary modules
from src.backend import check_engine,get_table_name_by_id
import sys

def update_portfolio(PORTFOLIO_ID, TRIG_UPDATE_WEIGHTS,TRIG_METH_EXP,
                     DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME):

    print(f'DB_USERNAME : {DB_USERNAME}')
    print(f'DB_PASSWORD : {DB_PASSWORD}')
    print(f'DB_HOST : {DB_HOST}')
    print(f'DB_PORT: {DB_PORT}')
    print(f'DB_NAME: {DB_PORT}')
    
    DATABASE_URL = f"postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    print(f'DATABASE URL: {DATABASE_URL}')

    try:
        engine = check_engine(DATABASE_URL)
        print('Checking tables in the database ...')
        table_name = get_table_name_by_id(engine, PORTFOLIO_ID)
        if table_name :
            print(f"The name of the table with {PORTFOLIO_ID} is : {table_name}")
        else :
            print('No table was found')
    except Exception as e:
        print(f"Connection failed: {e}")

    if TRIG_UPDATE_WEIGHTS :
        print('New weights will be computed')
    else : 
        print('No weights update')

    if TRIG_METH_EXP:
        print('We will use an average expense fee per stock')
    else:
        print('We will use an average expense fee per stock transaction')

if __name__ == '__main__':

    if len(sys.argv) < 8:
        print("Not enough input arguments")
        sys.exit(1)
    else :
        PORTFOLIO_ID = int(sys.argv[1])
        TRIG_UPDATE_WEIGHTS = bool(int(sys.argv[2]))
        TRIG_METH_EXP = bool(int(sys.argv[3]))
        DB_USERNAME = sys.argv[4]
        DB_PASSWORD = sys.argv[5]
        DB_HOST = sys.argv[6]
        DB_PORT = sys.argv[7]
        DB_NAME = sys.argv[8]

        update_portfolio(PORTFOLIO_ID, TRIG_UPDATE_WEIGHTS,TRIG_METH_EXP, 
                        DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
