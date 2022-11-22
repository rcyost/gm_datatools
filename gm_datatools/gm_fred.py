import pandas as pd
import fredpy as fp

def gm_test(data:list)-> pd.DataFrame:
    return pd.DataFrame({'col': data})

def get_fred_series(series:str, series_name:str, change:int= 0, convert:tuple[str, str]= ('', '')) -> pd.DataFrame:
    """_summary_

    Args:
        series (str): _description_
        series_name (str): _description_
        change (int, optional): _description_. Defaults to None.
        convert (tuple[str, str], optional): [0] is freq and [1] is agg type. Defaults to ('', '').
                    freq (string):      Abbreviation of desired frequency: 'D','W','M','Q','A'
                    method (string):    How to resample the data: 'first', 'last', 'mean' (default), 'median',
                                    'min', 'max', 'sum'
    """

    if ' ' in series_name:
        print("No spaces in series name please!")

    fp.api_key= '51c004fb3def8cab5ed38546d2651ad1'
    fred_series = fp.series(series)

    if convert is not ('', ''):
        fred_series= fred_series.as_frequency(convert[0], convert[1])

    fred_series= pd.DataFrame(fred_series.data).reset_index()
    fred_series.rename({'value': series_name}, axis=1, inplace=True)
    fred_series['date']= pd.to_datetime(fred_series['date'])

    # rate of change calculate
    if change != 0:
        fred_series[series_name]= fred_series[series_name].pct_change(change)

    return(fred_series)


def get_real_rates():
    fed_funds= get_fred_series('FEDFUNDS', 'fed_funds')
    fed_funds['fed_funds']= fed_funds['fed_funds'] / 100

    cpi= get_fred_series('CPIAUCSL', 'cpi_yoy', change=12)

    real_rates= pd.merge(
        left=fed_funds,
        left_on= 'date',
        right= cpi,
        right_on='date'
    )

    real_rates['real_rates']= real_rates['fed_funds'] - real_rates['cpi_yoy']
    real_rates= real_rates.set_index('date')
    return real_rates


