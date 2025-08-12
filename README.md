# Financial Statement API

A simple FastAPI application containerized with Docker that connects to the SEC.gov public API to retrieve financial data and calculate key financial metrics. This API provides fundamental company information and financial statement items to support company evaluation and analysis.

SEC.gov API documentation:  
https://www.sec.gov/search-filings/edgar-application-programming-interfaces

---

## Project Structure

/backend  
│── requirements.txt            # Python dependencies  
│── api/  
│   └── main.py                # FastAPI application entry point  
└── utils/  
    ├── depend_utils.py        # Support utility functions  
    └── financial_statement.py # 18 financial statement items  

/data  
│── result/  
│   └── sec_data_2021_to_2023.json  # SEC data from 2021 to 2023, quarterly, with 18 financial items for target companies  
│  
└── target/  
    └── sp500_with_cik_updated.csv   # Target companies merged with CIK based on original dataset  

/Dockerfile                      # Docker build instructions  

---

## Run the Docker Container

```bash
docker run -d -p 8000:8000 fincal_statement_api
```

### Access the API Documentation
Open your browser and visit : http://localhost:8000/docs 

---

## API Query
### Query Parameters
This structure represents the JSON response format for querying company financial data by tic, year, and quarter.
- tic : 'AAPL'
- year : 2023
- quarter : 'Q2'

---
## Result JSON Structure

| Field              | Type                | Description                                     |
|--------------------|---------------------|-------------------------------------------------|
| cik                | string              | Company CIK identifier, zero-padded (e.g., "0000320193") |
| tic                | string              | Ticker symbol of the company (e.g., "AAPL")    |
| company            | string              | Company name (e.g., "Apple Inc.")               |
| exchanges          | list of strings     | Stock exchange(s) where the company is listed (e.g., ["Nasdaq"]) |
| year               | integer             | Financial data year (e.g., 2023)                |
| quarter            | string              | Financial quarter (e.g., "Q2")                   |
| url                | string (URL) or null | Link to the SEC filing HTML document            |
| financial statement | object (dict)        | Financial metrics with values and status flags  |

### Financial Statement Object Structure

Each financial metric contains:

| Metric Name        | Type                  | Description                                      |
|--------------------|-----------------------|------------------------------------------------|
| val                | string, number or null| Value of the financial metric (e.g., "44.3%", 55862000000, or null) |
| stat               | integer (-1, 0, 1)    | Status indicator: 1 = good, -1 = bad, 0 = None data |

### Example of Financial Metrics and Their Judgment Rules

| Metric Name          | Description                    | Judgment Rule                  |
|----------------------|-------------------------------|-------------------------------|
| RevenueGrowth (%)    | Revenue growth rate            | > 10%                         |
| GrossMargin (%)      | Gross profit margin            | > 0*                          |
| NetProfitMargin (%)  | Net profit margin              | > 10%                         |
| OperatingMargin (%)  | Operating profit margin        | > 15%                         |
| EPSGrowth (%)        | Earnings per share growth      | (No specific rule)             |
| FCF (Free Cash Flow) | Free cash flow                 | > 0                           |
| ROE (%)              | Return on equity               | > 15%                         |
| ROA (%)              | Return on assets               | > 7%                          |
| CurrentRatio         | Current assets to liabilities  | > 1.5                         |
| QuickRatio           | Quick assets to liabilities    | > 1.0                         |
| DebtToEquityRatio    | Debt compared to equity        | < 1.0                         |
| EBIT                 | Earnings before interest & tax | > 0*                          |
| DSO (Days Sales Outstanding) | Average collection period | < 45 days                    |
| OCF (Operating Cash Flow) | Operating cash flow          | > 0                           |
| CFF (Cash Flow from Financing) | Cash flow from financing | < 0                          |
| DCR (Debt Coverage Ratio) | Debt coverage ratio           | > 2x                          |
| CapexRatio (CR)      | Capital expenditure ratio      | ≥ 1                           |
| ICR (Interest Coverage Ratio) | Interest coverage ratio     | > 5x                          |

_* Note: Since there is no single universal standard, basic criteria are applied where values are generally expected to be positive._


These rules are used to evaluate each financial metric's status, where typically:

- If the metric satisfies the rule, status is positive (stat = 1)  
- If it does not satisfy the rule, status is negative (stat = -1)  
- If data is missing or not finding, stat = 0 

### Sample JSON Response

```bash
{'cik': '0000320193',
 'tic': 'AAPL',
 'company': 'Apple Inc.',
 'exchanges': ['Nasdaq'],
 'year': 2023,
 'quarter': 'Q2',
 'url': 'https://www.sec.gov/Archives/edgar/data/0000320193/000032019323000064/aapl-20230401.htm',
 'financial statement': {'RevenueGrowth': {'val': '-19.1%', 'stat': -1},
  'GrossMargin': {'val': '44.3%', 'stat': 1},
  'NetProfitMargin': {'val': '25.5%', 'stat': 1},
  'OperatingMargin': {'val': '29.9%', 'stat': 1},
  'EPSGrowth': {'val': '-19.0%', 'stat': -1},
  'FCF': {'val': 55862000000, 'stat': 1},
  'ROE': {'val': '38.9%', 'stat': 1},
  'ROA': {'val': '7.3%', 'stat': 1},
  'CurrentRatio': {'val': 0.9, 'stat': -1},
  'QuickRatio': 0.9,
  'DebtToEquityRatio': {'val': 1.9, 'stat': -1},
  'EBIT': {'val': 28318000000, 'stat': 1},
  'DSO': {'val': '17.0 days', 'stat': 1},
  'OCF': {'val': 62565000000, 'stat': 1},
  'CapexRatio': {'val': 9.3, 'stat': 1},
  'CFF': {'val': -61287000000, 'stat': -1},
  'DCR': {'val': None, 'stat': 0},
  'ICR': {'val': 30.4, 'stat': 1}}
  }
  ```