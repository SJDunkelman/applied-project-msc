#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rank stocks within universe on equity factors.
"""

import pandas as pd

markets = ['HK','UK','DK','IT','US']

def GetFinancials(ticker,date,financial_df):
    released_financials_df = financial_df.loc[(financial_df.ticker == ticker) & (financial_df.period > date)]
    if len(released_financials_df) > 0:
        return released_financials_df.iloc[0]
    else:
        return None

for market in ['UK']: #markets
    # Load data
    price_filename = market + '_price_data.csv'
    price_data = pd.read_csv(price_filename)
    price_data.t = pd.to_datetime(price_data.t,format='%Y-%m-%d')
    financial_filename = market + '_financial_data.csv'
    financial_data = pd.read_csv(financial_filename)
    financial_data.period = pd.to_datetime(financial_data.period,format='%Y-%m-%d')
    
    # Create master dataframe for entire time series
    ticker_list = list(set(financial_data.ticker))
    market_date_time_series = price_data.t.loc[price_data.ticker == ticker_list[0]]
    
    