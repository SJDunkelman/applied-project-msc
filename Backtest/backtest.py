#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import math as m

factor_weights = pd.DataFrame(columns=['date','ticker','weight','position'])

# Helper functions


class Portfolio():
    def __init__(self,quality_weights,value_weights,size_weights,price_df,initial_value = 1000000):
        # Initialisation
        self.quality_weights = quality_weights
        self.value_weights = value_weights 
        self.size_weights = size_weights
        self.price_df = price_df
        self.portfolio_value = 0
        self.portfolio_cash = initial_value
        
        # Config
        self.transaction_cost = 1.003
        self.rebalance_interval = 1 # days
        
        # output
        self.holdings = pd.DataFrame(columns=['date','ticker','cost_amount','position_type'])
        self.value_time_series = pd.DataFrame(columns=['date','portfolio_value'])
    
    def GetDailyPositions(self,factor,date,position_type):
        if factor == 'q':
            return self.quality_weights.loc[(self.quality_weights['date'] == date) & (self.quality_weights['position'] == position_type)]
        elif factor == 'v':
            return self.value_weights.loc[(self.value_weights['date'] == date) & (self.value_weights['position'] == position_type)]
        elif factor == 's':
            return self.size_weights.loc[(self.size_weights['date'] == date) & (self.size_weights['position'] == position_type)]
    
    def RebalancePortfolio(self,date,factor_df):
        # Get target number of shares
        # if portfolio value = 0 (first day)
            # If cash
                # buy shares with cash
        pass

    def GetTargetNumberShares(self,weight,share_price):
        target_value = weight * self.portfolio_value
        return m.floor(target_value / (share_price * self.transaction_costs))
    
    def BuyLongShares(self,date,ticker,number_shares):
        share_price = self.price_df.o.loc[(self.price_df.ticker == ticker) & (self.price_df.date == date)]
        cost = (share_price * self.transaction_cost) * number_shares
        if self.portfolio_cash >= cost:
            self.portfolio_cash =- cost
            row = {'date':[date],'ticker':[ticker],'cost_amount':[cost],'position_type':['long']}
            self.holdings = self.holdings.append(row)
    
    def SellShortShares(self,date,ticker,number_shares):
        share_price = self.price_df.o.loc[(self.price_df.ticker == ticker) & (self.price_df.date == date)]
        cost = (share_price * self.transaction_cost) * number_shares
        if self.portfolio_cash >= cost:
            self.portfolio_cash =- cost
            row = {'date':[date],'ticker':[ticker],'cost_amount':[cost],'position_type':['short']}
            self.holdings = self.holdings.append(row)
            
    def SellLongShares(self,date,ticker,number_shares):
        share_price = self.price_df.o.loc[(self.price_df.ticker == ticker) & (self.price_df.date == date)]
        value = share_price * number_shares
        self.portfolio_cash =+ value
        row = {'date':[date],'ticker':[ticker],'cost_amount':[cost],'position_type':['long']}
        self.holdings = self.holdings.append(row)