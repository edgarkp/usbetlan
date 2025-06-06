""" A routine to populate database before deployment
List of stocks :
	- NOC (Northrop Grum..)
	- LMT (Lockheed Martin)
	- LDOS (Leidos Holdings)
	- BAH (Booz Alien Hami…)
	- DFEN (Direxion Dly Aer…)
	- EOG (Eog Res Inc)
	- CVX (Chevron Corp)
	- XOM (Exxon Mobil)
	- GM (General Motors Co)
	- TSLA (Tesla Inc)
	- PHUN (Phunware Inc)
    - DJT (Trump Media & …)

The election happening on 5th november, we suppose that the bet was made after the presidential debates
and stocks were bought the next Monday following these debates i.e. 7th October 

Generate data function will create the data from the 7th october to 20th december, friday before the app deployment date (23rd december)
"""

# before launching the app, ensure that a sql command was run to set the initial state of the 4 portofolios
"""
INSERT INTO portfolio_landry (
    timestamp,
    stocks_values,
    stocks_weights,
    gross_portfolio_value,
    total_transaction_fees,
    available_cash,
    net_portfolio_value,
    portfolio_return 
)
VALUES (    
    '2024-10-07',
    '{"NOC": 10000, "LMT": 10000, "LDOS": 10000, "BAH": 10000, "DFEN": 10000, "EOG": 10000, "CVX": 10000, "XOM": 10000, "GM": 10000, "TSLA": 10000, "PHUN": 10000, "DJT": 10000}'::JSONB,
  '{"NOC": 0.083, "LMT": 0.083, "LDOS": 0.083, "BAH": 0.083, "DFEN": 0.083, "EOG": 0.083, "CVX": 0.083, "XOM": 0.083, "GM": 0.083, "TSLA": 0.083, "PHUN": 0.083, "DJT": 0.083}'::JSONB,
    120000,
    0,
    0,
    120000,
    0.0
);

INSERT INTO portfolio_edgar_daily (
    timestamp,
    stocks_values,
    stocks_weights,
    gross_portfolio_value,
    total_transaction_fees,
    available_cash,
    net_portfolio_value,
    portfolio_return 
)
VALUES (    
    '2024-10-07',
    '{"NOC": 10000, "LMT": 10000, "LDOS": 10000, "BAH": 10000, "DFEN": 10000, "EOG": 10000, "CVX": 10000, "XOM": 10000, "GM": 10000, "TSLA": 10000, "PHUN": 10000, "DJT": 10000}'::JSONB,
  '{"NOC": 0.083, "LMT": 0.083, "LDOS": 0.083, "BAH": 0.083, "DFEN": 0.083, "EOG": 0.083, "CVX": 0.083, "XOM": 0.083, "GM": 0.083, "TSLA": 0.083, "PHUN": 0.083, "DJT": 0.083}'::JSONB,
    120000,
    0,
    0,
    120000,
    0.0
);

INSERT INTO portfolio_edgar_weekly (
    timestamp,
    stocks_values,
    stocks_weights,
    gross_portfolio_value,
    total_transaction_fees,
    available_cash,
    net_portfolio_value,
    portfolio_return 
)
VALUES (    
    '2024-10-07',
    '{"NOC": 10000, "LMT": 10000, "LDOS": 10000, "BAH": 10000, "DFEN": 10000, "EOG": 10000, "CVX": 10000, "XOM": 10000, "GM": 10000, "TSLA": 10000, "PHUN": 10000, "DJT": 10000}'::JSONB,
  '{"NOC": 0.083, "LMT": 0.083, "LDOS": 0.083, "BAH": 0.083, "DFEN": 0.083, "EOG": 0.083, "CVX": 0.083, "XOM": 0.083, "GM": 0.083, "TSLA": 0.083, "PHUN": 0.083, "DJT": 0.083}'::JSONB,
    120000,
    0,
    0,
    120000,
    0.0
);

INSERT INTO portfolio_edgar_monthly (
    timestamp,
    stocks_values,
    stocks_weights,
    gross_portfolio_value,
    total_transaction_fees,
    available_cash,
    net_portfolio_value,
    portfolio_return 
)
VALUES (    
    '2024-10-07',
    '{"NOC": 10000, "LMT": 10000, "LDOS": 10000, "BAH": 10000, "DFEN": 10000, "EOG": 10000, "CVX": 10000, "XOM": 10000, "GM": 10000, "TSLA": 10000, "PHUN": 10000, "DJT": 10000}'::JSONB,
  '{"NOC": 0.083, "LMT": 0.083, "LDOS": 0.083, "BAH": 0.083, "DFEN": 0.083, "EOG": 0.083, "CVX": 0.083, "XOM": 0.083, "GM": 0.083, "TSLA": 0.083, "PHUN": 0.083, "DJT": 0.083}'::JSONB,
    120000,
    0,
    0,
    120000,
    0.0
);

"""
# create a function that will take as input the datetime and identify which trigger is necessary and update the portfolio accordingly
from src.update_portfolio import update_portfolio
from datetime import date, timedelta
import holidays
import time
# import os
import sys


def get_input_update_portofolio(date):
    print("Updating the trigger variables")
    is_weekly = date.weekday() == 0  # Monday
    is_monthly = date.day == 1       # First day of the month

    trig_update_weights_1 = False # Always false
    trig_update_weights_2 = True   # Always true
    trig_update_weights_3 = is_weekly # Weekly
    trig_update_weights_4 = is_monthly  # Monthly
    
    return [trig_update_weights_1, trig_update_weights_2,trig_update_weights_3, trig_update_weights_4]

def update_portfolios(date, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME):
    trig_update_weights_list = get_input_update_portofolio(date)
    
    for index, trig in enumerate(trig_update_weights_list):
        print(f"Updating portfolios N°{index+1}")
        update_portfolio(index+1, 
                         trig,
                         False,
                         DB_USERNAME, 
                         DB_PASSWORD, 
                         DB_HOST, 
                         DB_PORT, 
                         DB_NAME,
                         date)
    

def generate_data(start, end, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME):
    nyse_holidays = set(holidays.NYSE(years=range(start.year, end.year + 1)))
    all_days = list([start])
    rest_days = [start + timedelta(x + 1) for x in range((end - start).days)]
    all_days.extend(rest_days)

    business_days = [day for day in all_days if day.weekday() < 5 and day not in nyse_holidays]
    print('Number of business days is:', len(business_days))

    for day in business_days:
        print(f"updating portfolios for day {day}")
        update_portfolios(day, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
        time.sleep(3)

if __name__ == '__main__':
    DB_USERNAME = sys.argv[1]
    DB_PASSWORD = sys.argv[2]
    DB_HOST = sys.argv[3]
    DB_PORT = sys.argv[4]
    DB_NAME = sys.argv[5] 

    ## Run this rest to complete the data filling
    start = date(2024, 10, 8)
    end = date(2024, 12, 26)

    print("Ready to generate data ...")
    generate_data(start, end, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)           
