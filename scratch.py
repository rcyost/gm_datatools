
#%%
import pandas as pd
from gm_datatools.gm_fred import get_fred_series


#%%



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

real_rates= get_real_rates()

real_rates