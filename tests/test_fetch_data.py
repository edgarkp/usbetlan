from src.data_preprocessing import fetch_data
import pandas as pd

list_stock = ['BNP.PA', 'IPS.PA']

def test_read_data_non_empty_dataframe_daily():

    result_daily = fetch_data(list_stock, '1d')

    #Assert for daily values
    assert result_daily[list_stock[0]] is not None
    assert result_daily[list_stock[1]] is not None

    assert isinstance(result_daily[list_stock[0]], pd.DataFrame)
    assert isinstance(result_daily[list_stock[1]], pd.DataFrame)

    assert not result_daily[list_stock[0]].empty
    assert not result_daily[list_stock[0]].empty

def test_read_data_non_empty_dataframe_minutes():

    result_minutes = fetch_data(list_stock, '1m')

    assert result_minutes[list_stock[0]] is not None
    assert result_minutes[list_stock[1]] is not None

    assert isinstance(result_minutes[list_stock[0]], pd.DataFrame)
    assert isinstance(result_minutes[list_stock[1]], pd.DataFrame)

    assert not result_minutes[list_stock[0]].empty
    assert not result_minutes[list_stock[0]].empty


