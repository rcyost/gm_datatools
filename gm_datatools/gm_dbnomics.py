
import requests
from dbnomics import fetch_series


# https://dbnomics.discourse.group/t/imf-weo-2022-missing/632/2
def fetch_num_pages(provider_code, page_num = 0, limit = 50):
    offset = page_num * limit
    provider_datasets_url = f'https://api.db.nomics.world/v22/datasets/{provider_code}?offset={offset}'
    response_json = requests.get(provider_datasets_url).json()
    num_found = response_json["datasets"]["num_found"]
    return num_found

# https://dbnomics.discourse.group/t/imf-weo-2022-missing/632/2
def fetch_providers_meta(provider_code, page_num = 0, limit = 50):
    offset = page_num * limit
    provider_datasets_url = f'https://api.db.nomics.world/v22/datasets/{provider_code}?offset={offset}'
    response_json = requests.get(provider_datasets_url).json()

    return response_json['datasets']['docs']

def get_all_datasets_metadata(provider_code:str):
    limit = 50
    num_found= fetch_num_pages(provider_code, page_num=0)
    num_pages = round(num_found / limit)
    all_meta= []
    for page_num in range(0, num_pages):
        provider_metadata= fetch_providers_meta(provider_code, page_num=page_num)
        all_meta= all_meta + provider_metadata

    return all_meta

def dataset_metadata(provider_code, dataset_code):
    datasets= get_all_datasets_metadata(provider_code)
    dataset_metadata= [e for e in datasets if e['code']==dataset_code]
    return dataset_metadata[0]

def get_dots(ref_area:list, counterpart_area:list, indicators:list, freq:list):
    """https://db.nomics.world/IMF/DOT

    Args:
        importers (list): _description_
        exporters (list): _description_
        indicators (list):
            [TBG_USD] Goods, Value of Trade Balance, US Dollars
            [TMG_CIF_USD] Goods, Value of Imports, Cost, Insurance, Freight (CIF), US Dollars
            [TMG_FOB_USD] Goods, Value of Imports, Free on board (FOB), US Dollars
            [TXG_FOB_USD] Goods, Value of Exports, Free on board (FOB), US Dollars
        freq (list): _description_
    """

    # if importers or exporters == ['all']:
    #     dots_meta= dataset_metadata('IMF', 'DOT')
    #     dots_countries= [c for c in dots_meta['dimensions_values_labels']['COUNTERPART_AREA'].keys()]

    #     if importers == ['all']:
    #         importers= dots_countries
    #     if exporters == ['all']:
    #         exporters= dots_countries

    raw_dots = fetch_series(
        provider_code='IMF',
        dataset_code='DOT',
        max_nb_series=10000000000,
        dimensions={
        "FREQ":freq,
        "REF_AREA":ref_area,
        "COUNTERPART_AREA":counterpart_area,
        "INDICATOR":indicators})

    return raw_dots

def get_weo_countries(weo_code= 'WEO:2022-10'):
    weo_meta= dataset_metadata('IMF', weo_code)
    weo_countries= [c for c in weo_meta['dimensions_values_labels']['weo-country'].keys()]
    return weo_countries

def get_weo(indicator:list, country:list, unit:list, weo_code:str= 'WEO:2022-10'):

    """https://db.nomics.world/IMF/WEO:2021-04

    Args:
        weo_code (str): _description_
        indicator (list): _description_
        country (list): _description_
        unit (list): _description_

    Returns:
        _type_: _description_
    """
    weo_ngdp_raw= fetch_series(
        provider_code='IMF',
        dataset_code=weo_code,
        # max it out to ensure we don't cut off any data
        max_nb_series=1000000,
        dimensions={
            "weo-subject":indicator,
            "weo-country":country,
            "unit":unit
        })

    return weo_ngdp_raw





#