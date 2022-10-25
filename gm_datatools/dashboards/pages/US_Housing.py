# Copyright 2018-2022 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

from gm_datatools import gm_fred

st.set_page_config(
    page_title="US Housing Market",
    page_icon="",
    layout='wide')


st.markdown("# US Housing Market")
st.sidebar.header("US Housing Market")

col1, col2 = st.columns(2)

df = pd.DataFrame({'col': [0,1,2,3,4]})

median_house_price_yoy= gm_fred.get_fred_series(
    series= 'MSPUS',
    series_name= 'median_house_price_yoy',
    change= 4)


shiller_home_price_yoy= gm_fred.get_fred_series(
    series= 'CSUSHPINSA',
    series_name= 'shiller_home_price_yoy',
    change= 12)

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(df)

######################################################################################################
####### Column 1
######################################################################################################

fig = px.line(df, template='simple_white')
# customize font and legend orientation & position
fig.update_layout(
    font_family="Garamond",
    plot_bgcolor='rgba(0,0,0,0)',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-.3,
        xanchor="right",
        x=0.5))

# Chart 1
col1.subheader("Chart 1")
col1.plotly_chart(fig)
col1.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='large_df.csv',
    mime='text/csv',
    key=0)

# Chart 3
col1.subheader("Chart 3")
col1.plotly_chart(fig)
col1.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='large_df.csv',
    mime='text/csv',
    key=1
)

######################################################################################################
####### Column 2
######################################################################################################

# Chart 2
col2.subheader("Chart 2")
col2.plotly_chart(fig)
col2.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='large_df.csv',
    mime='text/csv',
    key= 2
)

# Chart 4
col2.subheader("Chart 4")
col2.plotly_chart(fig)
col2.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='large_df.csv',
    mime='text/csv',
    key= 3)
