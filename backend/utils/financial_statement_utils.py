from utils.depend_utuls import get_fact_value,filter_with_accessionNumber

#main function
def get_financial_statement(companyFacts,accessionNumber,accessionNumber_last):
    facts_keys = companyFacts.json()['facts']['us-gaap'].keys()

    #RevenueGrowth(%)
    revenues_current = None
    revenues_last = None
    rg = None

    ## current quarter
    revenues_current = get_fact_value(companyFacts, facts_keys, 'Revenues', filter_with_accessionNumber, accessionNumber)
    if revenues_current is None : 
        revenues_current = get_fact_value(companyFacts, facts_keys, 'RevenueFromContractWithCustomerExcludingAssessedTax', filter_with_accessionNumber, accessionNumber)

    ## last quarter
    revenues_last = get_fact_value(companyFacts, facts_keys, 'Revenues', filter_with_accessionNumber, accessionNumber_last)
    if revenues_last is None : 
        revenues_last = get_fact_value(companyFacts, facts_keys, 'RevenueFromContractWithCustomerExcludingAssessedTax', filter_with_accessionNumber, accessionNumber_last)

    ## revenueGrowth
    rg = (revenues_current - revenues_last) / revenues_last *100  if revenues_current and revenues_last else None

    rg_status = 0 if rg is None else (1 if rg > 10 else -1)
    

    #GrossMargin(%)
    g_m = None
    gp = get_fact_value(companyFacts, facts_keys, 'GrossProfit', filter_with_accessionNumber, accessionNumber)

    ## grossmargin
    g_m = ((gp / revenues_current)*100) if gp and revenues_current else None

    g_m_status = 0 if g_m is None else (1 if g_m > 0 else -1)

    #NetProfitMargin(%)
    np_m = None
    np = get_fact_value(companyFacts, facts_keys, 'NetIncomeLoss', filter_with_accessionNumber, accessionNumber)

    ## netprofitmargin
    np_m = ((np / revenues_current)*100) if np and revenues_current else None

    np_m_status = 0 if np_m is None else (1 if np_m > 10 else -1)

    #OperatingMargin(%)
    op_m = None
    op = get_fact_value(companyFacts, facts_keys, 'OperatingIncomeLoss', filter_with_accessionNumber, accessionNumber)

    ## operatingmargin
    op_m = ((op / revenues_current)*100) if op and revenues_current else None

    op_m_status = 0 if g_m is None else (1 if g_m > 15 else -1)


    #EPSGrowth(%)
    eps_g = None
    ## current quarter
    eps_current = get_fact_value(companyFacts, facts_keys, 'EarningsPerShareBasic', filter_with_accessionNumber, accessionNumber)

    ## last quarter
    eps_last = get_fact_value(companyFacts, facts_keys, 'EarningsPerShareBasic', filter_with_accessionNumber, accessionNumber_last)

    ## epsgrowth
    eps_g = ((eps_current - eps_last) / eps_last *100) if eps_current and eps_last else None

    eps_g_status = 0 if eps_g is None else (1 if eps_g > 10 else -1)

    #FCF
    fcf = None
    ocf = get_fact_value(companyFacts, facts_keys, 'NetCashProvidedByUsedInOperatingActivities', filter_with_accessionNumber, accessionNumber) 

    ## tag = PaymentsToAcquirePropertyPlantAndEquipment
    cpex = get_fact_value(companyFacts, facts_keys, 'PaymentsToAcquirePropertyPlantAndEquipment', filter_with_accessionNumber, accessionNumber)

    ## tag = PurchasesOfPropertyAndEquipmentAndIntangibleAssets
    if cpex is None :
        cpex = get_fact_value(companyFacts, facts_keys, 'PurchasesOfPropertyAndEquipmentAndIntangibleAssets', filter_with_accessionNumber, accessionNumber) 

    fcf = ocf - cpex if ocf and cpex else None
    fcf_status = 0 if fcf is None else (1 if fcf > 0 else -1)

    #ROE(%)
    roe = None
    equity = get_fact_value(companyFacts, facts_keys, 'StockholdersEquity', filter_with_accessionNumber, accessionNumber)

    ## roe
    roe = ((np / equity)*100) if np and equity else None

    roe_status = 0 if roe is None else (1 if roe > 15 else -1)

    #ROA(%)
    roa = None
    assets = get_fact_value(companyFacts, facts_keys, 'Assets', filter_with_accessionNumber, accessionNumber)

    ## roa
    roa = ((np / assets)*100) if np and assets else None

    roa_status = 0 if roa is None else (1 if roa > 7 else -1)

    #CurrentRatio
    cur_r = None
    assets_c = get_fact_value(companyFacts, facts_keys, 'AssetsCurrent', filter_with_accessionNumber, accessionNumber)
    liabilities_c = get_fact_value(companyFacts, facts_keys, 'LiabilitiesCurrent', filter_with_accessionNumber, accessionNumber)
    cur_r = assets_c / liabilities_c if assets_c and liabilities_c else None

    cur_r_status = 0 if cur_r is None else (1 if cur_r > 1.5 else -1)


    #QuickRatio
    qu_r = None
    inventorynet = get_fact_value(companyFacts, facts_keys, 'InventoryNet', filter_with_accessionNumber, accessionNumber)
    qu_r = (assets_c - inventorynet) / liabilities_c if assets_c and inventorynet and liabilities_c else None

    qu_r_status = 0 if qu_r is None else (1 if qu_r > 1.0 else -1)

    #DebtToEquityRatio
    de_Eq_r = None
    de_Eq_r = liabilities_c / equity if liabilities_c and equity else None

    de_Eq_r_status = 0 if de_Eq_r is None else (1 if de_Eq_r < 1.0 else -1)

    #EBIT
    ebit = None
    ebit = get_fact_value(companyFacts, facts_keys, 'OperatingIncomeLoss', filter_with_accessionNumber, accessionNumber)
    ebit_status = 0 if ebit is None else (1 if ebit > 0 else -1)

    #DSO (days)
    dso = None
    accountsreceivable = get_fact_value(companyFacts, facts_keys, 'AccountsReceivableNetCurrent', filter_with_accessionNumber, accessionNumber)
    dso = 90 / (revenues_current / accountsreceivable) if accountsreceivable and revenues_current else None
    dso_status = 0 if dso is None else (1 if dso < 45 else -1)

    #OCF(Operatin Cash Flow)
    ocf = None
    ocf = get_fact_value(companyFacts, facts_keys, 'NetCashProvidedByUsedInOperatingActivities', filter_with_accessionNumber, accessionNumber) 
    ocf_status = 0 if ocf is None else (1 if ocf >0 else -1)

    #CR(CapexRatio)
    cr = None
    ## capitalexpenditures
    cpex = get_fact_value(companyFacts, facts_keys, 'PurchasesOfPropertyAndEquipmentAndIntangibleAssets', filter_with_accessionNumber, accessionNumber) 
    if cpex is None :
        cpex = get_fact_value(companyFacts, facts_keys, 'PaymentsToAcquirePropertyPlantAndEquipment', filter_with_accessionNumber, accessionNumber)
    cr = ocf / cpex if ocf and cpex else None
    cr_status = 0 if cr is None else (1 if cr >=1 else -1)

    #CFF(Cash Flow from Financing)
    cff = None
    cff = get_fact_value(companyFacts, facts_keys, 'NetCashProvidedByUsedInFinancingActivities', filter_with_accessionNumber, accessionNumber) 
    cff_status = 0 if ocf is None else (1 if ocf <0 else -1)

    #DCR(Debt Coverage Ratio)
    debt_long = None
    debt_current = None 

    debt_long = get_fact_value(companyFacts, facts_keys, 'LongTermDebtNoncurrent', filter_with_accessionNumber, accessionNumber) 
    debt_current = get_fact_value(companyFacts, facts_keys, 'DebtCurrent', filter_with_accessionNumber, accessionNumber) 
    debt = debt_long + debt_current if debt_long and debt_current else None
    dcr = ocf / debt if ocf and debt else None

    dcr_status = 0 if dcr is None else (1 if dcr >2 else -1)

    #ICR(Interest Coverage Ratio)
    icr = None
    interest = get_fact_value(companyFacts, facts_keys, 'InterestExpense', filter_with_accessionNumber, accessionNumber) 
    icr = op / interest if op and interest else None
    icr_status = 0 if icr is None else (1 if icr >5 else -1)

    financial_statement = {
        "RevenueGrowth": {'val': rg if not rg else f"{round(rg, 1)}%",'stat': rg_status},

        "GrossMargin": {'val': g_m if not g_m else f"{round(g_m, 1)}%",'stat': g_m_status},

        "NetProfitMargin": {'val': np_m if not np_m else f"{round(np_m, 1)}%",'stat': np_m_status},

        "OperatingMargin": {'val': op_m if not op_m else f"{round(op_m, 1)}%",'stat': op_m_status},

        "EPSGrowth": {'val': eps_g if not eps_g  else f"{round(eps_g, 1)}%",'stat': eps_g_status},

        'FCF': {'val':fcf,'stat':fcf_status},

        'ROE': {'val': roe if not roe else f"{round(roe, 1)}%",'stat':roe_status},

        'ROA': {'val': roa if not roa else f"{round(roa, 1)}%",'stat':roa_status},

        'CurrentRatio': {'val': cur_r if not cur_r else round(cur_r, 1),'stat':cur_r_status},

        'QuickRatio':  qu_r if not qu_r else round(qu_r, 1), 

        'DebtToEquityRatio': {'val': de_Eq_r if not de_Eq_r else round(de_Eq_r, 1),'stat':de_Eq_r_status},

        'EBIT': {'val':ebit,'stat':ebit_status},

        'DSO': {'val': dso if not dso else f"{round(dso, 1)} days",'stat':dso_status},

        'OCF': {'val': ocf,'stat':ocf_status},

        'CapexRatio': {'val': cr if not cr else round(cr, 1),'stat':cr_status},

        'CFF': {'val':cff,'stat':cff_status},

        'DCR': {'val': dcr if not dcr else round(dcr, 1),'stat':dcr_status},

        'ICR': {'val': icr if not icr else round(icr, 1),'stat':icr_status}
        }
    
    return financial_statement