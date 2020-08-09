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

# Initialisation
finnhub_client = fh.Client(api_key="br4je57rh5r8ufeothr0")
quandl.ApiConfig.api_key = "tGZHNrmk8QrR7yXGnT42"
tickers_df = pd.read_csv('failed_company_data.csv')
robur_codes_df = pd.read_csv('./rb1codes.csv')
robur_statements = ['BALANCE','CASHFLOW','INCOME']
yf.pdr_override()
backtest_start_date = '2019-06-01'
backtest_end_date = '2020-08-07'

# Helper functions
def GetISIN(ticker):
    return finnhub_client.company_profile(symbol=ticker)['isin']

def GetRoburCompanyCode(isin):
    return robur_codes_df.company_code.loc[robur_codes_df.isin == isin]

def GetQuandlCode(company_code,financial_statement):
    return "RB1/{company_code}_HY{financial_statement}".format(company_code,financial_statement)

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
for index, row in tickers_df.iterrows():
    isin = GetISIN(row.ticker)
    if row.reason_failed == 'financials':
        DownloadRoburFinancials(isin)
    else:
        print("Use yahoo finance to ")

# Get RB1 symbol from ISIN

# Get RB1 financial data from RB1 company symbol

