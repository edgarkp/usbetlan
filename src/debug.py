from src.update_portfolio import update_portfolio
from datetime import date
import os

DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

TRIG_UPDATE_WEIGHTS = True
TRIG_METH_EXP = True
PORTFOLIO_ID = 2

DATE = date(2024,10,21)

update_portfolio(PORTFOLIO_ID, TRIG_UPDATE_WEIGHTS,TRIG_METH_EXP,
                     DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DATE)