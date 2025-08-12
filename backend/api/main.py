import sys 
sys.path.insert(0,"./backend")

from fastapi import FastAPI, Query
import requests
import pandas as pd
from utils.depend_utuls import find_accessionNumber_targer,find_company_cik
from utils.financial_statement_utils import get_financial_statement

quarters_list = ['Q1', 'Q2', 'Q3', 'FY']

# Initialize FastAPI application
app = FastAPI()

@app.get("/get_sec_data")
def get_sec_data(
    ticker: str = Query(..., description="e.g. AAPL"),
    year: int = Query(..., description="e.g. 2021"),
    quarter: str = Query(..., description="e.g. Q1 or Q2 or Q3 or FY")
):
    cik = find_company_cik(ticker)
    quarter = quarter.strip()

    headers = {'User-Agent': "email@address.com"}

    # Retrieve filing metadata from SEC
    filingMetadata = requests.get(
        f'https://data.sec.gov/submissions/CIK{cik}.json',
        headers=headers
    )
    if filingMetadata.status_code != 200:
        return {"error": "CIK not found or SEC API error."}

    # Retrieve company facts from SEC
    companyFacts = requests.get(
        f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json',
        headers=headers
    )
    if companyFacts.status_code != 200:
        return {"error": "Company facts not found or SEC API error."}

    # Create a DataFrame mapping accession numbers to primary documents
    fi_df_primaryDocument = pd.DataFrame({
        'accessionNumber': filingMetadata.json()['filings']['recent']['accessionNumber'],
        'primaryDocument': filingMetadata.json()['filings']['recent']['primaryDocument']
    })

    # Extract the first available DEI tag and its latest unit type
    dei_tag = list(companyFacts.json()['facts']['dei'].keys())[0]
    units_tag = list(companyFacts.json()['facts']['dei'][dei_tag]['units'].keys())[-1]
    sec_data = companyFacts.json()['facts']['dei'][dei_tag]['units'][units_tag]

    # Basic company information
    cik_num = filingMetadata.json()['cik']
    tic_symbol = filingMetadata.json()['tickers'][0]
    com_name = filingMetadata.json()['name']
    exchanges = filingMetadata.json()['exchanges']

    # Find accession numbers for the target year and previous year
    df_accessionNumber = find_accessionNumber_targer(fi_df_primaryDocument, sec_data, year, quarters_list)
    df_accessionNumber_last = find_accessionNumber_targer(fi_df_primaryDocument, sec_data, (year - 1), quarters_list)

    # Map current year accession numbers by quarter
    accn_dict_current = {}
    if not df_accessionNumber.empty:
        for q in quarters_list:
            match = df_accessionNumber.loc[df_accessionNumber['quarter'] == q, 'accessionNumber']
            accn_dict_current[q] = match.iloc[0] if not match.empty else None

    # Map previous year accession numbers by quarter
    accn_dict_last = {}
    if not df_accessionNumber_last.empty:
        for q in quarters_list:
            match = df_accessionNumber_last.loc[df_accessionNumber_last['quarter'] == q, 'accessionNumber']
            accn_dict_last[q] = match.iloc[0] if not match.empty else None

    # Select accession numbers based on the requested quarter
    if quarter == 'Q1':
        accessionNumber = accn_dict_current.get('Q1', None)
        accessionNumber_last = accn_dict_last.get('FY', None)
    else:
        accessionNumber = accn_dict_current.get(quarter, None)
        accessionNumber_last = accn_dict_current.get(
            quarters_list[quarters_list.index(quarter) - 1], None
        )

    # Match the corresponding primary document for the quarter
    match_primaryDocument = None
    if not df_accessionNumber.empty:
        match_doc_series = df_accessionNumber.loc[df_accessionNumber['quarter'] == quarter, 'primaryDocument']
        match_primaryDocument = match_doc_series.iloc[0] if not match_doc_series.empty else None

    # Construct SEC filing URL
    match_accessionNumber = accessionNumber
    url = f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{match_accessionNumber.replace('-', '')}/{match_primaryDocument}" if match_accessionNumber and match_primaryDocument else None

    # Retrieve financial statement data
    financial_statement = get_financial_statement(companyFacts, accessionNumber, accessionNumber_last)

    # Prepare response payload
    sec_data = {
        'cik': cik_num,
        'tic': tic_symbol,
        'company': com_name,
        'exchanges': exchanges,
        'year': year,
        'quarter': quarter,
        'url': url,
        'financial statement': financial_statement
    }

    return sec_data
