#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reconcile missing FinnHub data with Robur financial data.
"""

import finnhub as fh
import pandas as pd
import yfinance as yf
import pandas_datareader as pdr
import quandl
import time

# Initialisation
finnhub_client = fh.Client(api_key="br4je57rh5r8ufeothr0")
quandl.ApiConfig.api_key = "tGZHNrmk8QrR7yXGnT42"
# tickers_df = pd.read_csv('failed_company_data.csv')
robur_codes_df = pd.read_csv('./rb1codes.csv')
robur_statements = ['BALANCE','CASHFLOW','INCOME']
yf.pdr_override()
backtest_start_date = '2019-06-01'
backtest_end_date = '2020-08-07'

# Helper functions
def GetISIN(ticker):
    company_profile = finnhub_client.company_profile(symbol=ticker)
    if len(company_profile) > 0:
        return company_profile['isin']
    else:
        return None

def GetRoburCompanyCode(isin):
    robur_search = robur_codes_df.company_code.loc[robur_codes_df.isin_code == isin]
    if len(robur_search) > 0:
        return robur_search.iloc[0]
    else:
        return None

def GetQuandlCode(company_code,financial_statement):
    return "RB1/{company_code}_HY{financial_statement}".format(company_code=company_code,financial_statement=financial_statement)

def MergeStatementDF(statement_df_list):
    output = statement_df_list[0].merge(statement_df_list[1],on="period")
    output = output.merge(statement_df_list[2],on="period")
    output = output.set_index('period')
    return output

def DownloadRoburFinancials(isin):
    statement_df_list = []
    for statement in robur_statements:
        company_code = GetRoburCompanyCode(isin)
        quandl_code = GetQuandlCode(company_code,statement)
        statement_data = quandl.get(quandl_code,
                                    start_date = backtest_start_date,
                                    end_date = backtest_end_date)
        statement_df_list.append(statement_data)
    return MergeStatementDF(statement_df_list)
        
def DownloadPriceData(ticker):
    return pdr.get_data_yahoo(ticker,
                              start = backtest_start_date,
                              end = backtest_end_date)

# Get ISIN from Finnhub symbol
# for index, row in tickers_df.iterrows():
#     isin = GetISIN(row.ticker)
#     if row.reason_failed == 'financials':
#         DownloadRoburFinancials(isin)
#     elif row.reason_failed == 'price':
#         continue

# Get RB1 symbol from ISIN

# Get RB1 financial data from RB1 company symbol
        
# Check what % of companies are on Robur
ticker_df = pd.concat(pd.read_excel('investment_universe.xlsx', sheet_name=None), ignore_index=True)
def MapRoburCodes(ticker_df):
    robur_code_mapping = pd.DataFrame(columns=['ticker','robur_code'])
    ticker_count = 0
    for ticker in ticker_df.finnhub:
        row = {}
        print("Checking",ticker)
        row['ticker'] = ticker
        isin = GetISIN(ticker)
        ticker_count += 1
        if (ticker_count+1) % 30 == 0:
            time.sleep(60)
        if isin is not None:
            robur_company_code = GetRoburCompanyCode(isin)
            if robur_company_code is not None:
                row['robur_code'] = robur_company_code
            else:
                row['robur_code'] = 'N/A'
        else:
            row['robur_code'] = 'N/A'
        robur_code_mapping = robur_code_mapping.append(row,ignore_index=True)
    return robur_code_mapping
        
    # print("Robur has ",str((counter / len(ticker_df.finnhub))*100),"% of company data needed")
MapRoburCodes(ticker_df)