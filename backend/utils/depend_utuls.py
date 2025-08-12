import pandas as pd
import requests

# utils function 

## depends on main
def find_accessionNumber_targer(fi_df_primaryDocument,sec_data,year_t,quarters_list):
    """
    To find and merge the search list data with the accessionNumber and primaryDocument.
    """
    last_y = next(item for item in reversed(sec_data) if item['fy'] != None)['fy']
    first_y = next(item for item in sec_data if item['fy'] != None)['fy']
    if first_y < year_t and last_y >= year_t:
        sec_data = [item for item in sec_data if item['fy'] == year_t and item['fp'] in quarters_list ]

        fi_df = pd.DataFrame(sec_data)
        fi_df = fi_df.rename(columns={'accn': 'accessionNumber','fp': 'quarter'})[['accessionNumber', 'form', 'quarter']]
        fi_df = fi_df.merge(fi_df_primaryDocument[['accessionNumber', 'primaryDocument']],on='accessionNumber',how='left')

        return(fi_df)
    else:
        fi_df = pd.DataFrame()
        return(fi_df)
    
## depends on main    
def find_company_cik(tic):
    """
    Find the company CIK number based on the ticker symbol.
    """
    import requests

    ticker = tic.upper()
    headers = {
        "User-Agent": "Your Name (your.email@example.com)"
    }
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=headers)
    sec_data = response.json()

    cik_str = None
    for item in sec_data.values():
        if item['ticker'].upper() == ticker:
            cik_str = str(item['cik_str']).zfill(10)
            break
    return cik_str

## depands on "get_financial_statement"
def check_with_statement(sec_data,year):
    """
    To check if the search year is included in the SEC data years.
    """
    if [item for item in sec_data if item['fy'] == year ]:
        return True
    else:
        return False

def filter_with_accessionNumber(sec_data,accessionNumber):
    """
    Filter financial data based on accessionNumber.
    """
    sec_data = [item for item in sec_data if item['accn'] == accessionNumber ]
    return sec_data

def get_fact_value(companyFacts, facts_keys, tag_name, filter_with_accessionNumber, accessionNumber):
    """
    To get the financial statement items (factors).
    """
    if not accessionNumber:
        return None
    
    if tag_name not in facts_keys:
        return None
    units_keys = list(companyFacts.json()['facts']['us-gaap'][tag_name]['units'].keys())[0]
    fact_data = companyFacts.json()['facts']['us-gaap'][tag_name]['units'][units_keys]
    fact_data = filter_with_accessionNumber(fact_data,accessionNumber)
    
    if not fact_data:  # empty list
        return None
    
    return fact_data[-1]['val']