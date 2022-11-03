"""
Helper functions to get data out of BLS
9/13/2022
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import BytesIO

# very important to making this system folder relative
# allowing it to run on different computers
import pathlib
current_path= pathlib.Path(__file__).parent.resolve()

def download_metadata(database: str, meta:str):

    metadata_url= f'https://download.bls.gov/pub/time.series/{database}/{database}.{meta}'
    r = requests.get(metadata_url)
    df= pd.read_csv(BytesIO(r.content), sep="\t")
    df.columns= [col.strip() for col in df.columns]

    return df

def download_survey_data(database: str, survey:str):

    survey_url= f'https://download.bls.gov/pub/time.series/{database}/{database}.data.{survey}'
    # get data and store as txt

    r = requests.get(survey_url)
    df= pd.read_csv(BytesIO(r.content), sep="\t")
    df.columns= [col.strip() for col in df.columns]
    df['series_id']= df['series_id'].str.strip()

    return df

def databases_list(survey:str):
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
