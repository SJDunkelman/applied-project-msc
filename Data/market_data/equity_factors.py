#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 17:43:02 2020

@author: simondunkelman
"""

import pandas as pd
import numpy as np

# Helper functions
def RankComponents(**kwargs):
    max_length = max(len(x) for x in kwargs.values())
    final_rank = np.zeros(max_length)
    for column in kwargs.values():
        column_ranked = column.rank(numeric_only=True,na_option='keep',ascending=True)
        final_rank += column_ranked
    return final_rank / (max_length  + 1)
        
def UpperDecile(df,factor_column_name):
    upper_decile_index = df.quantile(.9)[factor_column_name]
    output = df.iloc[int(upper_decile_index):]
    return output

def LowerDecile(df,factor_column_name):
    lower_decile_index = df.quantile(.1)[factor_column_name]
    output = df.iloc[:int(lower_decile_index)]
    return output

"""
Equity Quality factor

Profitability:
 - ROE = Net Income / Average Shareholder equity
 - Operating cash flow / Total Assets
 - Accruals = accounts receivable - (accounts payable + payable accrued)

Safety:
 - Debt / EBITDA
 - Asset leverage = Debt / Total Assets

Shareholder-friendly management:
 - Share Buybacks
"""

def EquityQuality(net_income,
                  shareholder_equity,
                  operating_cash_flow,
                  total_assets,
                  # accruals,
                  ebitda,
                  total_debt,
                  share_buybacks):
    # Calculate every metric in a dictionary
    metrics = {'return_on_equity' : net_income / shareholder_equity,
               'cash_flow_to_assets' : operating_cash_flow / total_assets,
               #'accruals' : 
               'debt_to_earnings' : total_debt / ebitda,
               'asset_leverage' : total_debt / total_assets,
               'share_buybacks' : share_buybacks
               }
    return pd.DataFrame(metrics)

# load sample data
sample_price = pd.read_csv('checkpoint_price_data.csv')
sample_financial = pd.read_csv('checkpoint_financial_data.csv')

quality = EquityQuality(metrics['return_on_equity'])