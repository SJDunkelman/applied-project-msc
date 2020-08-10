#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rank stocks within universe on equity factors.
"""

import pandas as pd
import datetime
from equity_factors import Company

markets = ['HK','UK','DK','IT','US']

def UnixToDate(unix):
    return datetime.datetime.utcfromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S')

def GetFinancials(ticker,date_time,financial_df):
    released_financials_df = financial_df.loc[(financial_df.ticker == ticker) & (financial_df.period < date_time)]
    if len(released_financials_df) > 0:
        return released_financials_df.iloc[0]
    else:
        return None
    
def GetPrice(ticker,unix_date,price_df):
    return price_df.loc[(price_df.ticker == ticker) & (price_df.t == unix_date)].iloc[0].loc[['c','h','l','o','t','v']]

def CalculateDailyFactors(ticker_list,unix_date,financials_df,price_df):
    daily_factors_df = pd.DataFrame()
    for ticker in ticker_list:
        company_price = GetPrice(ticker,unix_date,price_df)
        company_share_price = company_price.o
        date_time = UnixToDate(unix_date)
        company_financials = GetFinancials(ticker,date_time,financials_df)
        if company_financials is not None:
            company = Company(ticker,company_financials,company_share_price,'fh')
            company_quality = company.EquityQuality()
            company_quality['ticker'] = ticker
            daily_factors_df = daily_factors_df.append(company_quality)
        else:
            print("No financial data for",ticker)
    return daily_factors_df
        
def GetLongestTimeSeriesTicker(ticker_list,price_df):
    length_ticker = {}
    for ticker in ticker_list:
        length_ticker.__setitem__(ticker, len(price_data.t.loc[price_data.ticker == ticker]))
    return max(length_ticker,key = length_ticker.get)

def GetDailyTickers(price_df,unix_date):
    return list(set(price_data.ticker.loc[price_data.t == unix_date]))

for market in ['UK']: #markets
    # Load data
    price_filename = './without_removals/' + market + '_price_data.csv'
    price_data = pd.read_csv(price_filename)
    # price_data.t = pd.to_datetime(price_data.t,unit='s')
    financials_filename = './without_removals/' + market + '_financial_data.csv'
    financials_data = pd.read_csv(financials_filename)
    financials_data.period = pd.to_datetime(financials_data.period,format='%Y-%m-%d')
    
    # Create master dataframe for entire time series
    ticker_list = list(set(price_data.ticker))
    market_date_time_series = price_data.t.loc[price_data.ticker == GetLongestTimeSeriesTicker(ticker_list,price_data)]
    
    master_quality_factor_time_series = pd.DataFrame()
    master_size_factor_time_series = pd.DataFrame()
    master_value_factor_time_series = pd.DataFrame()
    
    # Get DF of financial data for single day of each stock
    test_date = 1596697200 # DEBUG
    test_date_list = [test_date] # DEBUG
    for date in test_date_list: # change to => market_date_time_series
        daily_ticker_list = GetDailyTickers(price_data,date)
        daily_data = CalculateDailyFactors(daily_ticker_list,date,financials_data,price_data)


            