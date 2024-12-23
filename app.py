# Import necessary modules
from src.update_portfolio import update_portfolio
from datetime import date
import sys

if __name__ == '__main__':

    if len(sys.argv) < 8:
        print("Not enough input arguments")
        sys.exit(1)

    else:
        PORTFOLIO_ID = int(sys.argv[1])
        TRIG_UPDATE_WEIGHTS = bool(int(sys.argv[2]))
        TRIG_METH_EXP = bool(int(sys.argv[3]))
        DB_USERNAME = sys.argv[4]
        DB_PASSWORD = sys.argv[5]
        DB_HOST = sys.argv[6]
        DB_PORT = sys.argv[7]
        DB_NAME = sys.argv[8]

        DATE = date.today()
        
        update_portfolio(PORTFOLIO_ID, TRIG_UPDATE_WEIGHTS,TRIG_METH_EXP, 
                        DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DATE)
