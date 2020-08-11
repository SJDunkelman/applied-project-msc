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

class Company():
    def __init__(self,ticker,financials_df,share_price,data_source):
        self.share_price = share_price # Need to get latest price for share price
        self.ticker = ticker
        
        if data_source == 'fh':
            self.revenue = self.ValidateInput('revenue',financials_df)
            self.net_income = self.ValidateInput('netIncome',financials_df)
            self.total_assets = self.ValidateInput('totalAssets',financials_df)
            self.total_debt = self.ValidateInput('totalDebt',financials_df)
            self.shareholder_equity = self.total_assets - self.total_debt
            self.operating_cash_flow = self.ValidateInput('cashfromOperatingActivities',financials_df)
            self.ebitda = self.ValidateInput('netIncomeBeforeTaxes',financials_df)
            self.shares_outstanding = self.ValidateInput('totalCommonSharesOutstanding',financials_df)
            self.dividend_yield = self.ValidateInput('totalCashDividendsPaid',financials_df) / self.shares_outstanding
            self.market_cap = self.shares_outstanding * self.share_price
            self.cash_and_equivalents = self.ValidateInput('cash',financials_df) + self.ValidateInput('cashEquivalents',financials_df)
            self.enterprise_value = self.market_cap + self.total_debt + self.cash_and_equivalents
            self.book_value = self.shares_outstanding * self.ValidateInput('tangibleBookValueperShare',financials_df)
        elif data_source == 'rb':
            self.net_income = financials_df['Net Income exc. extra'],
            self.total_assets = financials_df['Total Assets'],
            self.total_debt = financials_df['Total Liabilities'],
            self.shareholder_equity = self.total_assets - self.total_debt,
            self.operating_cash_flow = financials_df['Cash from Operations'],
            self.ebitda = financials_df['Operating Income']
            self.shares_outstanding = financials_df['Diluted Shares OS']
            self.market_cap = self.shares_outstanding * share_price
            self.cash_and_equivalents = financials_df['End Cash']
            self.enterprise_value = self.market_cap + self.total_debt + self.cash_and_equivalents
            self.book_value = financials_df['Shareholder Equity']
        else:
            print("Data source not recognised")
            
    def ValidateInput(self,variable_name,input_df):
        input_df = input_df.fillna(0)
        return input_df[variable_name]
    
    def EquityQuality(self):
        metrics = {'return_on_equity' : [self.net_income / self.shareholder_equity],
               'cash_flow_to_assets' : [self.operating_cash_flow / self.total_assets],
               'debt_to_earnings' : [self.total_debt / self.ebitda],
               'asset_leverage' : [self.total_debt / self.total_assets]
               }
        return pd.DataFrame.from_dict(metrics)
    
    def EquitySize(self):
        metrics = {'market_cap' : self.market_cap,
               'enterprise_value' : self.enterprise_value,
               'total_assets' : self.total_assets
               }
        return pd.DataFrame(metrics)
    
    def EquityValue(self):
        metrics = {'dividend_yield' : self.dividend_yield,
                   'earnings_to_price' : (self.net_income / self.shares_outstanding) / self.share_price,
                   'book_to_price' : (self.book_value / self.shares_outstanding) / self.share_price,
                   'sales_to_price' : (self.revenue / self.shares_outstanding) / self.share_price,
                   'enterprise_to_ebitda' : self.enterprise_value / self.ebitda
            }
        return pd.DataFrame(metrics)

    # def EquityMomentum(self):
    #     metrics

