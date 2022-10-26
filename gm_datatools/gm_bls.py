"""
Helper functions to get data out of BLS
9/13/2022
"""

from unittest.util import strclass
import requests
import pandas as pd
from bs4 import BeautifulSoup

# very important to making this system folder relative
# allowing it to run on different computers
import pathlib
current_path= pathlib.Path(__file__).parent.resolve()

def download_metadata(database: str, list_metadata_urls:list[str]):

    for meta in list_metadata_urls:

        metadata_url= f'https://download.bls.gov/pub/time.series/{database}/{database}.{meta}'

        r = requests.get(metadata_url)
        with open(f'{current_path}/{database}/metadata/{database}_{meta}.txt', 'wb') as f:
            f.write(r.content)

        df = pd.read_csv(f'{current_path}/{database}/metadata/{database}_{meta}.txt', sep="\t")
        df.columns= [col.strip() for col in df.columns]
        # strip columns if they have whitespace
        # for col in df.columns:
        #     if df[col].dtype == 'O':
        #         df[col]= df[col].str.strip()

        return df

def download_survey_data(database: str, survey:str):

    survey_url= f'https://download.bls.gov/pub/time.series/{database}/{database}.data.{survey}'
    # get data and store as txt
    r = requests.get(survey_url)
    with open(f'{current_path}/{database}/data/{survey}.txt', 'wb') as f:
        f.write(r.content)

    # open txt file, clean and store as csv
    df = pd.read_csv(f'{current_path}/{database}/data/{survey}.txt', sep="\t")
    df.columns= [col.strip() for col in df.columns]
    df['series_id']= df['series_id'].str.strip()

    return df

def get_data(table_name:str, series_code=None, series_name=None) -> pd.DataFrame:
    data= pd.read_csv(f"{current_path}/{table_name}")
    # filter for specific series
    if series_code!=None:
        data= data[data['series_id']==series_code]

    # clean dates
    data['period']= data.period.str[1:]
    data['date']= data.period +'-'+ data.year.astype(str)
    data= data[data['period'] != '13']
    data['date']= pd.to_datetime(data['date'])
    if series_name:
        data.rename({'value': series_name},axis=1, inplace=True)

    return data


def download_data_series(survey:str):
        # scrape html off bls page
        survey_url= f'https://download.bls.gov/pub/time.series/{survey}/'
        r = requests.get(survey_url)
        soup = BeautifulSoup(r.content)

        # links with "data." in then are data series
        data_list= []
        for a in soup.find_all('a', href=True):
                if 'data.' in a['href']:
                        data_list.append(a['href'].split('data.')[1])

        return data_list
