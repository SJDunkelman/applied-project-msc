#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data collection from FinnHub.
"""

import finnhub as fh
import pandas as pd
from datetime import datetime
from datetime import timezone
import time

finnhub_client = fh.Client(api_key="br4je57rh5r8ufeothr0")

# Helper functions
def DateToUnix(date):
    return int(date.replace(tzinfo=timezone.utc).timestamp())
        
def FlattenStatementDF(statement_df):
    list_of_dict = list(statement_df.financials)
    return pd.DataFrame(list_of_dict)

def MergeStatementDF(statement_df_list):
    output = statement_df_list[0].merge(statement_df_list[1],on="period")
    output = output.merge(statement_df_list[2],on="period")
    output = output.set_index('period')
    return output

def SaveOutput(filename_prefix,**kwargs):
    for df_name, df in kwargs.items():
        filename = filename_prefix + '_' + df_name + '.csv'
        df.to_csv(filename)

def FinnHubCode(ticker,market):
    return ticker + '.' + market

def GetFailedCompanies(failed_ticker_list,ticker_company_table,reason_failed):
    print("Couldn't get",reason_failed,"data for",len(failed_ticker_list),"companies.")
    output = pd.DataFrame(columns=['ticker','company','reason_failed'])
    for ticker in failed_ticker_list:
        company = ticker_company_table.company.loc[ticker_company_table.finnhub == ticker]
        row = {'ticker':ticker,'company':company,'reason_failed':reason_failed}
        output = output.append(row,ignore_index=True)
    return output
    
# FinnHub API functions
def GetPrice(client,ticker,start_unix,end_unix):
    candles = client.stock_candles(ticker, 'D', start_unix, end_unix)
    if candles['s'] == 'no_data':
        print("Could not find price data for",ticker)
        return None
    else:
        return pd.DataFrame(candles)

def GetFinancials(client,ticker,frequency,backtest_start_date):
    def _GetRelevantStatementIndex_(statement_df,backtest_start_date):
        # Flag if date of statement is within backtesting period
        def CheckDate(date_to_check,date_window):
            date_to_check = datetime.strptime(date_to_check, '%Y-%m-%d')
            return date_to_check >= date_window
        
        index = 0
        while index < len(statement_df):
            statement_date = statement_df.iloc[index][0]['period']
            if CheckDate(statement_date,backtest_start_date):
                index += 1
            else:
                return index + 1 # Include first statement out of period
        return index
    
    statement_type_list = ['bs','ic','cf']
    statement_df_list = []
    for statement_type in statement_type_list:
        statement_data_full = client.financials(ticker,statement_type,frequency)
        if statement_data_full['financials'] is None:
            print("Could not find financial data for",ticker)
            return None
        else:
            statement_data_full = pd.DataFrame(statement_data_full)
            statement_relevant_index = _GetRelevantStatementIndex_(statement_data_full,backtest_start_date)
            statement_data_relevant = statement_data_full.iloc[:statement_relevant_index]
            statement_df_list.append(FlattenStatementDF(statement_data_relevant))
    return MergeStatementDF(statement_df_list)
    

# Backtest parameters
start_date = datetime(2019,7,1) # 6 months prior to Covid-19
end_date = datetime(2020,8,7)

# Calculate UNIX Timestamps
"""
As UNIX timestamps are for midnight, the end_unix will give prices for day BEFORE end_date
"""
start_unix = DateToUnix(start_date)
end_unix = DateToUnix(end_date)

# Load finnhub codes for multiple investment universes
hong_kong = pd.read_excel('investment_universe.xlsx',sheet_name="HK")
united_kingdom = pd.read_excel('investment_universe.xlsx',sheet_name="GB")
denmark = pd.read_excel('investment_universe.xlsx',sheet_name="DK")
italy = pd.read_excel('investment_universe.xlsx',sheet_name="IT")
united_states = pd.read_excel('investment_universe.xlsx',sheet_name="US")

# Group by country
markets = {}
markets["HK"] = hong_kong
markets["L"] = united_kingdom
markets["CO"] = denmark
markets["MI"] = italy
markets["US"] = united_states

# Get price data for investment universe
master_price_data = pd.DataFrame(columns=['c', 'h', 'l', 'o', 's', 't', 'v','ticker','market'])
master_financial_data = pd.DataFrame()
failed_company_data = pd.DataFrame(columns=['ticker','company','reason_failed'])

for market, universe in markets.items():
    ticker_no_price_data = [] # Reconciliation
    ticker_no_financial_data = [] # Reconciliation
    
    ## Debug
    if market == 'HK'or market == 'L' or market == 'CO' or market == 'MI': #  
        continue
    ##
    
    # Get list of stocks
    ticker_list = list(universe.finnhub)
    print("\n\nExtracting data for",market,"\n\n")
    for ticker in ticker_list:
        # Get price data
        print("Extracting",ticker,"price")
        stock_price_data = GetPrice(finnhub_client,ticker,start_unix,end_unix)
        if stock_price_data is not None:
            stock_price_data['ticker'] = ticker
            stock_price_data['market'] = market
            # Add to master data DF
            master_price_data = master_price_data.append(stock_price_data)
        else:
            ticker_no_price_data.append(ticker)
        
        # Get financial statement data
        print("Extracting",ticker,"financials")
        stock_financial_data = GetFinancials(finnhub_client,ticker,'quarterly',start_date)
        if stock_financial_data is not None:
            stock_financial_data['ticker'] = ticker
            stock_financial_data['market'] = market
            # Add to master data DF
            master_financial_data = master_financial_data.append(stock_financial_data)
        else:
            ticker_no_financial_data.append(ticker)
            
        # Sleep every 4 tickers to avoid timeout
        if (ticker_list.index(ticker)+1) % 10 == 0:
            completion_percent = ((ticker_list.index(ticker)+1) / len(ticker_list))*100
            print("\n",str(completion_percent),"% complete\n")
            time.sleep(60)
        
    # Save companies that failed to download for price and financials
    failed_company_data = failed_company_data.append(GetFailedCompanies(ticker_no_price_data,universe,"price"))
    failed_company_data = failed_company_data.append(GetFailedCompanies(ticker_no_financial_data,universe,"financials"))
    SaveOutput(market,failed_company_data = failed_company_data)
    
    
    # Save price data as excel
    print("\n\nSaving Checkpoint...")
    filename = 'checkpoint_' + market
    SaveOutput(filename,
               price_data = master_price_data,
               financial_data = master_financial_data)
    time.sleep(60)
    
# Save price data as excel
print("\n\nSaving data...")
SaveOutput('master',
           price_data = master_price_data,
           financial_data = master_financial_data)
