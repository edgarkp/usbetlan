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


# create a function that will take as input the datetime and identify which trigger is necessary and update the portfolio accordingly
from src.update_portfolio import update_portfolio
import os
from datetime import date, timedelta


def get_input_update_portofolio(date):
    print(date)
    print(date.utcnow())
    is_weekly = date.weekday() == 0  # Monday
    is_monthly = date.day == 1       # First day of the month

    trig_update_weights_1 = False # Always false
    trig_update_weights_2 = True   # Always true
    trig_update_weights_3 = is_weekly # Weekly
    trig_update_weights_4 = is_monthly  # Monthly
    
    return [trig_update_weights_1, trig_update_weights_2,trig_update_weights_3, trig_update_weights_4]

def update_portfolios(date):
    trig_update_weights_list = get_input_update_portofolio(date)

    for index, trig in enumerate(trig_update_weights_list):
        update_portfolio(index, 
                         trig,
                         False,
                         os.getenv['DB_USERNAME'], 
                         os.getenv['DB_PASSWORD'], 
                         os.getenv['DB_HOST'], 
                         os.getenv['DB_PORT'], 
                         os.getenv['DB_NAME'])

# use the above function to loop all the datetimes from the 8th october to 20th december
start = date(2024, 10, 8)
end = date(2024, 12, 20)

# get list of all days
all_days = [start + timedelta(x + 1) for x in range((end - start).days)]

# filter business days
# weekday from 0 to 4. 0 is monday adn 4 is friday
# increase counter in each iteration if it is a weekday
count = sum(1 for day in all_days if day.weekday() < 5)
print('Number of business days is:', count)

for day in all_days:
    if day.weekday() < 5:
        update_portfolios(day)
