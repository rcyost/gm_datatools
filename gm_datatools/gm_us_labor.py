import pandas as pd
import streamlit as st

from gm_datatools import gm_fred

from .gm_bls import download_survey_data, download_metadata

# download data into folder
high_level=[
    10000000, 20000000,
    30000000, 40000000,
    50000000, 55000000,
    60000000, 65000000,
    70000000, 80000000,
    90000000]

indy_rename_dict={
    10000000:'mining_and_logging',
    20000000:'construction',
    30000000:'manufacturing',
    40000000:'trade_transportation_utils',
    50000000:'information',
    55000000:'fin_services',
    60000000:'prof_buis_services',
    65000000:'education_health',
    70000000:'leisure_hospitality',
    80000000:'other_services',
    90000000:'gov'
}

@st.experimental_memo
def create_wages_dash_data(indy_data:pd.DataFrame):
    all_wages= indy_data[indy_data.index.get_level_values(2) == 'S']
    all_wages= all_wages[['all_emp_wage_bill', 'product_nonsup_wage_bill', 'nonproduct_sup_wage_bill']]
    all_wages= (all_wages
        .reset_index()
        .pivot_table(
            columns= ['industry_code'],
            index= 'date',
            values= ['all_emp_wage_bill', 'product_nonsup_wage_bill', 'nonproduct_sup_wage_bill']
        )
        .dropna()
    )

    all_wages= all_wages.rename(indy_rename_dict, axis=1)
    total_wages= all_wages.groupby(level = 0, axis = 1).sum()
    total_new_wages= pd.Series(
        total_wages['all_emp_wage_bill'] - total_wages['all_emp_wage_bill'].shift()
    )

    return all_wages, total_wages, total_new_wages

@st.experimental_memo
def create_jobs_dash_data(indy_data:pd.DataFrame):
    employees= indy_data[indy_data.index.get_level_values(2) == 'S']
    # 1 is the total number of employees
    employees= pd.DataFrame(employees[1])

    employees= (employees
        .pivot_table(
            columns= 'industry_code',
            index= 'date',
            values= 1
        )
    )

    employees= employees.rename(indy_rename_dict, axis=1)

    (employees
        .query('index == @employees.index.max()')
        .T
    )

    employees_total= employees.sum(axis=1)
    employees_mom= employees.pct_change(1)
    employees_yoy= employees.pct_change(12)

    return employees, employees_mom, employees_yoy, employees_total

@st.experimental_memo
def create_dashboard_data(indy_data: pd.DataFrame) -> None:

    # total, indy; wages
    create_wages_dash_data(indy_data)

    # total, indy; jobs, new jobs
    create_jobs_dash_data(indy_data)

@st.experimental_memo
def download_ce_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """download all needed data for the us labor market

    data is need to explore the total wage bill,
    which there are a few ways to go about this

    1. total nonfarm employees * avg weekly earnings * 52
    2. aggregate weekly earnings * 52

    All data queried:
        - employees
        - avg weekly earnings

    By:
        - production / nonproduction workers
        - all employees
        - nonfarm
            - nonfarm needs to be
              calculated from raw data

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: ce_data, and ce_series
    """

    ce_series= download_metadata('ce', 'series')

    indy_series= (ce_series
        # we only want the highlest level of each sector
        .query('industry_code.isin(@high_level)')
        # non-industry based sectors (goods, services)
        # .query('~supersector_code.isin([5,6,7,8])')
        # different wages to get total wage bill
        # 56 is agg weekly hours , 11 is avg weekly earnings
        # production and non supervisory: 7 is hours, 30 is earnigs
        # 1 is total employees
        .query('data_type_code.isin([1, 2, 6, 7, 8, 11, 30, 38, 56, 57, 82])'))


    indy_series['series_id']= indy_series['series_id'].str.strip()


    ce_all_data= download_survey_data('ce', '0.AllCESSeries')

    indy_data= (ce_all_data
            .query('series_id.isin(@indy_series["series_id"])')
            .reset_index(drop=False)
    )

    # did we get all of the needed data?
    assert indy_data['series_id'].nunique() == indy_series['series_id'].nunique()

    indy_data= pd.merge(
        left= indy_data,
        right= indy_series[['series_id', 'industry_code', 'data_type_code', 'seasonal']],
        left_on= 'series_id',
        right_on= 'series_id',
    )

    indy_data= ((indy_data
        .pivot_table(
            index= ['date', 'industry_code', 'seasonal'],
            columns= ['data_type_code'],
            values= 'value'))
    )

    # return ce_series
    return indy_data, indy_series



#############################################################
###      WAGES
#############################################################

@st.experimental_memo
def calculate_wage_bill(indy_data:pd.DataFrame) -> pd.DataFrame:

    # 57 - AGGREGATE WEEKLY PAYROLLS OF ALL EMPLOYEES, THOUSANDS
    indy_data['all_emp_wage_bill']= indy_data[57] * 52

    # 82 - AGGREGATE WEEKLY PAYROLLS OF PRODUCTION AND NONSUPERVISORY EMPLOYEES, THOUSANDS
    indy_data['product_nonsup_wage_bill']= indy_data[82] * 52

    indy_data['nonproduct_sup_wage_bill']= indy_data['all_emp_wage_bill'] - indy_data['product_nonsup_wage_bill']
    return indy_data

@st.experimental_memo
def all_wages(wage_bill:pd.DataFrame) -> pd.DataFrame:

    all_wages= wage_bill[wage_bill.index.get_level_values(2) == 'S']

    all_wages= all_wages[['all_emp_wage_bill', 'product_nonsup_wage_bill', 'nonproduct_sup_wage_bill']]

    all_wages= (all_wages
        .reset_index()
        .pivot_table(
            columns= ['industry_code'],
            index= 'date',
            values= ['all_emp_wage_bill', 'product_nonsup_wage_bill', 'nonproduct_sup_wage_bill']
        )
        .dropna()
    )

    all_wages= all_wages.rename(indy_rename_dict, axis=1)

    return all_wages

@st.experimental_memo
def total_wages(wage_bill:pd.DataFrame) -> pd.DataFrame:

    temp= all_wages(wage_bill)

    return temp.groupby(level = 0, axis = 1).sum()

@st.experimental_memo
def calculate_real_wages(wage_bill:pd.DataFrame) -> pd.DataFrame:

    cpi_head_yoy= cpi_head_yoy= gm_fred.get_fred_series(
        series='CPIAUCSL',
        series_name='cpi_head_yoy',
        change= 12
    )

    all_wages= all_wages(wage_bill)
    all_wages= all_wages.rename(indy_rename_dict, axis=1)
    all_wage_yoy= all_wages.pct_change(12)

    real_wages= pd.merge(
        left= all_wage_yoy,
        right= cpi_head_yoy,
        left_index=True,
        right_index= True)

    real_wages= (real_wages
        .dropna())

    real_wages= real_wages.sub(real_wages['cpi_head_yoy'], axis=0)

    real_wages_all= real_wages.drop('cpi_head_yoy', axis=1)

    return real_wages, real_wages_all

@st.experimental_memo
def twb_agg_weekly(ce_all_data:pd.DataFrame) -> pd.DataFrame:
    # CES0500000057    Aggregate weekly payrolls of all employees, thousands, total private, seasonally adjusted
    twb= ce_all_data.query('series_id=="CES0500000057"')
    twb['twb']= twb['value'] * 52
    twb= twb[['value', 'twb']]
    twb= twb.rename({'value':'agg_week_payrolls'}, axis=1)

    twb= twb.set_index(['date'])
    twb= twb.sort_index(ascending=False)

    return twb

@st.experimental_memo
def twb_sup(ce_all_data) -> pd.DataFrame:
    all= twb_avg_weekly_num_emp(
        ce_all_data,
        'CES0500000011',
        'CES0500000001')

    production= twb_avg_weekly_num_emp(
        ce_all_data,
        earn_code= 'CES0500000030',
        num_emp_code= 'CES0500000006')

    sup= pd.merge(
        left= all,
        left_index=True,
        right= production,
        right_index=True
    )

    sup['sup_employees']= sup['num_employees_x'] - sup['num_employees_y']
    sup['twb_sup']= sup['twb_x'] - sup['twb_y']
    sup['avg_earn_sup']= sup['twb_sup'] / sup['sup_employees'] / 52
    sup= sup.sort_index(ascending=True)

    sup['num_employees_pct_change']= sup.pct_change(12)['sup_employees']
    sup['avg_weekly_earn_pct_change']= sup.pct_change(12)['avg_earn_sup']
    sup['twb_sup_pct_change']= sup.pct_change(12)['twb_sup']

    sup['twb_abs_change']= sup['twb_sup'] - sup['twb_sup'] .shift()

    sup= sup.sort_index(ascending=False)

    return sup[['sup_employees', 'twb_sup', 'avg_earn_sup', 'num_employees_pct_change', 'avg_weekly_earn_pct_change', 'twb_sup_pct_change','twb_abs_change']]

@st.experimental_memo
def twb_avg_weekly_num_emp(ce_all_data, earn_code:str, num_emp_code:str) -> pd.DataFrame:
    # CES0500000011 Average weekly earnings of all employees, total private, seasonally adjusted
    all_emp_earn= ce_all_data.query('series_id==@earn_code')

    #CES0000000001  All employees, thousands, total nonfarm, seasonally adjusted
    #all_emp_num= ce_all_data.query('series_id=="CES0000000001"')

    #CES0500000001  All employees, thousands, total private, seasonally adjusted
    all_emp_num= ce_all_data.query('series_id==@num_emp_code')

    twb= pd.merge(
        left= all_emp_num,
        left_index=True,
        right=all_emp_earn,
        right_index=True,
    )

    twb['twb']= twb['value_x'] * twb['value_y'] * 52

    twb= twb[['value_x', 'value_y', 'twb']]

    twb= twb.rename({'value_x':'num_employees', 'value_y':'avg_weekly_earn'}, axis=1)

    twb['num_employees_pct_change']= twb.pct_change(12)['num_employees']
    twb['avg_weekly_earn_pct_change']= twb.pct_change(12)['avg_weekly_earn']
    twb['twb_pct_change']= twb.pct_change(12)['twb']

    twb['twb_abs_change']= twb['twb'] - twb['twb'] .shift()

    twb= twb.sort_index(ascending=False)

    return twb

#############################################################
###      EMPLOYEES
#############################################################

@st.experimental_memo
def employees(indy_data, indy_series) -> pd.DataFrame:
    employees= indy_data[indy_data.index.get_level_values(2) == 'S']
    # 1 is the total number of employees
    employees= pd.DataFrame(employees[1])

    employees= (employees
        .pivot_table(
            columns= 'industry_code',
            index= 'date',
            values= 1
        )
    )

    employees= employees.rename(indy_rename_dict, axis=1)

    return employees



