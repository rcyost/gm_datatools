
#%%
import pandas as pd
from gm_datatools.gm_fred import get_fred_series


#%%

fed_funds= get_fred_series('FEDFUNDS', 'fed_funds')
fed_funds['fed_funds']= fed_funds['fed_funds'] / 100

cpi= get_fred_series('CPIAUCSL', 'cpi_yoy', change=12)

pd.merge(
    left=fed_funds,
    left_on= 'date',
    right= cpi,
    right_on='date'
)


