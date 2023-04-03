# https://www.youtube.com/watch?v=Vi-BQx4gE3k&t=793s
#

from BaseHelper import BaseHelper
import concurrent.futures as cf
from yahoofinancials import YahooFinancials
import time
from datetime import date, timedelta
from marketsenum import markets_enum
import logging
from GraphHelper import GraphHelper
from DataInterfaceHelper import dataInterfaceHelper
from datetime import datetime, timedelta

import pandas as pd
import yahoo_fin.stock_info as si
import re

from collections import Counter
import tradingExcpetions as tex

class ValueInvestingHelper2(BaseHelper):
    
    ratio_stat_select='"TotalDebtEquity","Diluted_EPS","TrailingAnnualDividendYield_perc","ForwardAnnualDividendYield_perc","ReturnOnEquity_perc","ReturnOnAssets_perc"'
    ratio_valuation_select='"Price/Book","Trailing-PE","Forward-PE","PEGRatio-5yr-expected","Price-Sales"'
    
    ratio_valuation_function=['Market Cap (intraday)', 'Price/Book (mrq)','Trailing P/E','Forward P/E','PEG Ratio (5 yr expected)',
                              'Price/Sales (ttm)', 'Enterprise Value/Revenue', 'Enterprise Value/EBITDA' ]
    ratio_stat=['Total Debt/Equity (mrq)', 'Diluted EPS (ttm)', 'Trailing Annual Dividend Yield 3','Forward Annual Dividend Yield 4', 
                'Ex-Dividend Date 4','Forward Annual Dividend Rate 4', '% Held by Insiders 1','% Held by Institutions 1',
                'Return on Equity (ttm)','Return on Assets (ttm)', 'Beta (5Y Monthly)', 'Quarterly Earnings Growth (yoy)',
                'Revenue (ttm)','Revenue Per Share (ttm)','Gross Profit (ttm)','EBITDA','Net Income Avi to Common (ttm)',
                'Total Cash (mrq)','Total Cash Per Share (mrq)','Total Debt (mrq)', '52-Week Change 3',
                'Current Ratio (mrq)','Book Value Per Share (mrq)','Operating Cash Flow (ttm)','Levered Free Cash Flow (ttm)']
    ratio_valuation_table=pd.DataFrame()
    ratio_stat_table=pd.DataFrame()

    def __init__(self):
        BaseHelper.__init__(self)
        
    def getStatsData(self, df, ticker):
        data=si.get_stats(ticker.tickerYahoo)
        data['Value'] = data['Value'].astype(str)
        data.index=data["Attribute"]
        data=data.drop(labels="Attribute",axis=1)
        raw_table=data.T
        print(raw_table)
        print(raw_table.iloc[0]['Shares Outstanding 5'])
        SharesOutstanding = self.__largeValConversion(raw_table.iloc[0]['Shares Outstanding 5'])
        return SharesOutstanding
        
    def __largeValConversion(self, x):
        print(x)
        if not x:
            return ""
        elif x=='nan' or pd.isna(x):
            return '0'
        
        try:
            if x.endswith('T'):
                return str(float(x.replace('T',''))*1000000000000000000)
            elif x.endswith("B"):
                return str(float(x.replace('B',''))*1000000000)
            elif x.endswith('M'):
                return str(float(x.replace('M',''))*1000000)
            elif x.endswith('k'):
                return str(float(x.replace('k',''))*1000)
            else:
                return x
        except Exception as e:
            print(e)
        
    
    def __buildCashData(self,ticker, marketE):
        cashStatement={}
        yahoo_financials = YahooFinancials(ticker.tickerYahoo)
        cash_statement_data = yahoo_financials.get_financial_stmts("annual", "cash")           

        for bs in cash_statement_data["cashflowStatementHistory"][ticker.tickerYahoo]:
            print(bs)
            theDate = ""
            for key, value in bs.items():
                theDate = key
            df = pd.DataFrame.from_dict(bs, orient="index")
            df["date"] = theDate
            df.rename(columns={list(df)[0]: "date"}, inplace=True)
            df['market']=marketE.name
            df["epic"] = ticker.ticker
            df.drop(df.columns.difference(['freeCashFlow', 'epic', 'market', 'date']), 1, inplace=True)
            print(df)
            try:
                df.to_sql(
                    "ratio_cash",
                    con=BaseHelper.engine,
                    if_exists="append",
                    index=False,
                )
                BaseHelper.session.commit()
            except Exception as e:
                logging.getLogger().debug(str(e))
                raise tex.InvalidDataException
    
            
    def __buildStatsValuationData(self, ticker, marketE):
        try:
            extra_ratio=si.get_stats_valuation(ticker.tickerYahoo)
            print(extra_ratio)
            extra_ratio.index=extra_ratio[0]
            extra_ratio=extra_ratio.drop(labels=0,axis=1)
        
            new_table=extra_ratio.T
            new_table["epic"] =  ticker.ticker
            new_table['market']=marketE.name
            new_table['date']=datetime.now().date()
            print(self.getStatsData(new_table, ticker))
            new_table['SharesOutstanding'] = self.getStatsData(new_table, ticker)
            new_table.rename(
                columns={
                    'Market Cap (intraday)': 'Market-Cap-Intraday-B',
                    'Enterprise Value': 'Enterprise-Value-B',
                    'Price/Book (mrq)': 'Price/Book',
                    'Trailing P/E': 'Trailing-PE',
                    'Forward P/E': 'Forward-PE',
                    'PEG Ratio (5 yr expected)': 'PEGRatio-5yr-expected',
                    'Price/Sales (ttm)': 'Price-Sales',
                    'Enterprise Value/Revenue': 'Enterprise-Value-Revenue',
                    'Enterprise Value/EBITDA': 'Enterprise-Value-EBITDA'
                },
                inplace=True,
            )
            print(new_table)
        
            new_table['Market-Cap-Intraday-B'] = new_table['Market-Cap-Intraday-B'].map(lambda x: str(self.__largeValConversion(x)))
            new_table['Enterprise-Value-B'] = new_table['Enterprise-Value-B'].map(lambda x: str(self.__largeValConversion(x)))
            print(new_table)
            new_table.to_sql(
                "ratio_valuation",
                con=BaseHelper.engine,
                if_exists="append",
                index=False,
            )
            BaseHelper.session.commit()
        except Exception as e:
            print(e)
            raise tex.InvalidDataException
    
    def __buildStatsData(self, ticker, marketE):
        data=si.get_stats(ticker.tickerYahoo)
        data.index=data["Value"]
        print(data)
        try:
            data['Value'] = data['Value'].astype(str)
            data['Value'] = data['Value'].map(lambda x: x.rstrip('%'))
            data['Value'] = data['Value'].map(lambda x: str(self.__largeValConversion(x))  )
            print(data)
            data.index=data["Attribute"]
            data=data.drop(labels="Attribute",axis=1)
            print(data)
            raw_table=data.T
            raw_table=raw_table[self.ratio_stat]
            raw_table["epic"] =  ticker.ticker
            raw_table['market']=marketE.name
            raw_table['date']=datetime.now().date()
 
            raw_table.rename(
                columns={
                    'Diluted EPS (ttm)':'Diluted_EPS',
                    'Trailing Annual Dividend Yield 3': 'TrailingAnnualDividendYield_perc',
                    'Forward Annual Dividend Yield 4': 'ForwardAnnualDividendYield_perc', 
                    '% Held by Insiders 1': 'HeldbyInsiders_perc',
                    '% Held by Institutions 1': 'HeldbyInstitutions_perc',
                    'Return on Equity (ttm)': 'ReturnOnEquity_perc',
                    'Return on Assets (ttm)':'ReturnOnAssets_perc',
                    'Beta (5Y Monthly)': 'BetaMonthly',
                    'Forward Annual Dividend Rate 4': 'ForwardAnnualDividendRate', 
                    'Ex-Dividend Date 4':'ExDividendDate',
                    'Revenue (ttm)':'Revenue',
                    'Revenue Per Share (ttm)':'RevenuePerShare',
                    'Gross Profit (ttm)':'GrossProfit',
                    'EBITDA':'EBITDA',
                    'Net Income Avi to Common (ttm)':'NetIncomeAviToCommon',
                    'Total Cash (mrq)':'TotalCash',
                    'Total Cash Per Share (mrq)':'TotalCashPerShare',
                    'Total Debt (mrq)':'TotalDebt',
                    'Total Debt/Equity (mrq)':'TotalDebtEquity',
                    'Current Ratio (mrq)':'CurrentRatio',
                    'Book Value Per Share (mrq)':'BookValuePerShare',
                    'Operating Cash Flow (ttm)':'OperatingCashFlow',
                    'Levered Free Cash Flow (ttm)':'LeveredFreeCashFlow',
                    '52-Week Change 3': '52-WeekChange',
                    'Quarterly Earnings Growth (yoy)' :'QuarterlyEarningsGrowth'              
                },
                inplace=True,
                )
        except Exception as e:
            print(e)
            raise tex.InvalidDataException
       
    
        #self.ratio_valuation_table=self.ratio_valuation_table.append(raw_table) 
        
        try:
            raw_table.to_sql(
                "ratio_stat",
                con=BaseHelper.engine,
                if_exists="append",
                index=False,
            )
            BaseHelper.session.commit()
        except Exception as e:
            print(str(e))
            logging.getLogger().debug(str(e))
        

    def __getYahooData(self, ticker, marketE):
        
        print("++getYahooData")
        print("processing "+ticker.ticker)
        # self.__buildStatsData(ticker, marketE)
        # self.__buildStatsValuationData(ticker, marketE)
        self.__buildCashData(ticker, marketE)
        
    def getNewData(self, marketE):
        tickers = self.getTickersList(marketE)
        
        # self.engine.execute("DELETE FROM ratio_stat WHERE market='"+marketE.name+"'")
        # self.engine.execute("DELETE FROM ratio_valuation WHERE market='"+marketE.name+"'")
        self.engine.execute("DELETE FROM ratio_cash WHERE market='"+marketE.name+"'")       
        BaseHelper.session.commit()

        executor = cf.ThreadPoolExecutor(1)
        futures = [executor.submit(self.__getYahooData, ticker, marketE) for ticker in tickers]
        cf.wait(futures)
              
    def __getOutstandingShares(self, ticker, marketE):
        ss="SELECT * FROM ratio_valuation where epic='"+ticker.ticker+"' and market='"+marketE.name+"'"
        df = pd.read_sql_query("SELECT * FROM ratio_valuation where epic='"+ticker.ticker+"' and market='"+marketE.name+"'", BaseHelper.conn)  
        print(df)
        if df.empty:
            return None
        else:
            sharesOutstanding= df.iloc[0]['SharesOutstanding']
            return sharesOutstanding
        
    def __getQuantitiveInvestmentData(self, ticker, marketE):
        dd="SELECT {} FROM public.ratio_stat WHERE epic='{}' and market={};".format(self.ratio_stat_select,ticker.ticker, marketE.name, BaseHelper.conn)
        dfStats = pd.read_sql_query("SELECT {} FROM public.ratio_stat WHERE epic='{}' and market='{}';".format(self.ratio_stat_select,ticker.ticker, marketE.name), BaseHelper.conn)
        dfVal = pd.read_sql_query("SELECT {} FROM public.ratio_valuation WHERE epic='{}' and market='{}';".format(self.ratio_valuation_select,ticker.ticker, marketE.name), BaseHelper.conn)

        print(dfVal)
        if dfVal.empty or dfStats.empty:
            return pd.DataFrame()
        else:
            final=pd.concat([dfVal,dfStats],axis=1)
            return final
        
    def __getQuantitiveInvestment(self, ticker, marketE):
        
        final=self.__getQuantitiveInvestmentData(ticker, marketE)
        if final.empty:
            return []
                
        # 1. Businesses which are quoted at low valuations

        # Let's find the companies which have their Trailing Price to earnings ratio less than 30 and Price to book value at less than 15
        # Thus, the condition is P/E < 30 P/B < 15

        #However, these ratios would differ from sector to sector, but for simplicity I’m using this numbers.

        final = final[(final['Trailing-PE'].astype(float)<40) & (final['Price/Book'].astype(float) < 15)]
        print(final)

        # 2. Businesses which have demonstrated earning power

        # I have kept the condition that the earnings per share is more than 4

        final = final[final['Diluted_EPS'].astype(float) > 4]
        print(final)

        # 3. Businesses earning good returns on equity while employing little or no debt

        # I am keeping the Debt to Equity ratio at 75 and Return on equity at more than 20%.
        # Note that Yahoo finance reports Debt to equity ratio in percentage. Thus, the figure 75 means it is 75% or o.75.

        final=final[(final['TotalDebtEquity'].astype(float)< 75 )] # Filter for Debt to Equity
        print(final)
        final=final[(final['ReturnOnEquity_perc'].astype(float)>20 )] # Filter for ROE
        print(final)
        return final
    
    # We pass in a list of dates and get the oddone out that has different months and day
    def __oddOneOutDate(self, arr):
        foundRef=None
        sDates=[]
        for d in arr:
            sDates.append(str(d.month)+"-"+str(d.day))
        previous=0
        next=0
        for i in range(0, len(sDates)):
            previous = i - 1
            next = i + 1
            if(i == len(sDates) - 1):
                next = 0;

            if(sDates[i] != sDates[previous] and sDates[i] != sDates[next]) :
                foundRef=i;
                break
        if foundRef != None:
            return arr[foundRef]
        else:
            return None
            
    
    def __getCashFlow(self, ticker, marketE):
        ss="SELECT * FROM ratio_cash where epic='"+ticker.ticker+"' and market='"+marketE.name+"'  ORDER BY date"
        df = pd.read_sql_query("SELECT * FROM ratio_cash where epic='"+ticker.ticker+"' and market='"+marketE.name+"' ORDER BY date", BaseHelper.conn)   # type: ignore
        if df.empty:
            raise tex.ValueInvestmentOutofDateException
        # Clean Data. remove cash flow that has a null value and if we have 5 dates remove the 
        allDates=df["date"].to_list()
        df1=df.dropna() # remove any free cahs flows that no value
        print(df1)
        if len(df1.index) > 4: # need to remove unwanted entries
            remDate=self.__oddOneOutDate(allDates)
            if remDate != None:
                df1 = df1.loc[df1["date"] != remDate]
                print(df1)
        
        if len(df1.index) == 4:  
            cashFlowDiv=[] 
            cashFlow = df1['freeCashFlow'].to_list()            
            for x in cashFlow: # We have to divide by a 1000 to get the calculation to work
                cashFlowDiv.append(x/1000)
            return cashFlowDiv
        else:
            return None
        
    def __getValueInvestmentsFairValue(self, ticker, marketE):
        print("++getValueInvestments")
        dih = dataInterfaceHelper()
        required_rate=0.07 # required investment rate of 7%
        #A perpetuity is a type of annuity that lasts forever, into perpetuity. 
        # The stream of cash flows continues for an infinite amount of time. In finance, 
        # a person uses the perpetuity calculation in valuation methodologies to find the 
        # present value of a company's cash flows when discounted back at a certain rate.
        perptual_rate=0.02 
        cashflowgrowthrate=0.03
        
        freecashflow = self.__getCashFlow(ticker, marketE)
        if freecashflow is None:
            return None

        years=[1,2,3,4]

        futurefreecashflow=[]
        discountfactor=[]
        discountedfuturefreecashflow=[]

        terminalvalue=freecashflow[-1]*(1+perptual_rate)/(required_rate-perptual_rate)

        print(terminalvalue)

        for year in years:
            cashflow=freecashflow[-1]*(1+cashflowgrowthrate)**year
            futurefreecashflow.append(cashflow)
            discountfactor.append((1+required_rate)**year)
            
        print(futurefreecashflow)
        print(discountfactor)

        for i in range(0, len(years)):
            discountedfuturefreecashflow.append(futurefreecashflow[i]/discountfactor[i])
            
        print(discountedfuturefreecashflow)

        dicsountterminalvalue=terminalvalue/(1+required_rate)**4
        discountedfuturefreecashflow.append(dicsountterminalvalue)

        todaysvalue=sum(discountedfuturefreecashflow)
        
        outstandingShares=self.__getOutstandingShares(ticker, marketE)

        fairvalue=todaysvalue*1000/outstandingShares
        #We need to get the last known value from DB
        previousClose = dih.getPreviousDayClose(ticker, marketE, datetime.now() - timedelta(days=1))
        if fairvalue > previousClose:
            return fairvalue, previousClose,((fairvalue-previousClose)/previousClose)*100
        else:
            return None, None, None
    
    def calculateValueInvestment(self,marketE,tickers=None):
        valInvList= pd.DataFrame()
        valueInvTickers=[]
        if tickers==None:
            tickers = self.getTickersList(marketE)
        for ticker in tickers:
            fairValue, prevClose, percenatgeGain = self.__getValueInvestmentsFairValue(ticker, marketE)
            final = self.__getQuantitiveInvestment(ticker, marketE)
            if fairValue != None and not final.empty:
                final["fair Value"]=round(fairValue,2)
                final["prev Close"]=round(prevClose,2)
                final["% gain"]=round(percenatgeGain,2)
                final['epic']=ticker.ticker
                final.index=final['epic']
                valInvList=pd.concat([valInvList,final])
                valueInvTickers = ticker.ticker
        if not valInvList.empty: # clean table
            valInvList.rename(
                columns={
                "TrailingAnnualDividendYield_perc": "TrailingAnnualDividendYield %",
                "ForwardAnnualDividendYield_perc":  "ForwardAnnualDividendYield %",
                "PEGRatio-5yr-expected": "PEGRatio-5yr",
                "ReturnOnEquity_perc": "ReturnOnEquity %",
                "ReturnOnAssets_perc":"ReturnOnAssets %"
            },
            inplace=True,
            )
        print(valInvList)
        valInvList.to_csv("ValueInv.csv")
        return valueInvTickers, valInvList
          
            
        
        
        # process the data
        # We need:
        # 1. Shares Outstanding << from yahoo_fin.stock_info.get_stats_valuation
        # 2. free cash flow for 4 years << from yahoo_financials.get_financial_stmts("annual", "cash")
        # 3. perptual_rate <<< Given value
        # 4. required_rate=0.07  <<< Given value
        # 5. cashflowgrowthrate=0.03  <<< Given value
        # PART 2
        # 1. Return on Equity (ttm) << from yahoo_fin.stock_info.get_stats
        # 2. Total Debt/Equity (mrq) << from yahoo_fin.stock_info.get_stats
        # 3. Diluted EPS (ttm) << from yahoo_fin.stock_info.get_stats
        # 4. Trailing P/E << from yahoo_fin.stock_info.get_stats_valuation
        # 5. Price/Book (mrq)  << from yahoo_fin.stock_info.get_stats_valuation
        
        
        
        
        
if __name__ == "__main__":
    
        vi = ValueInvestingHelper2()
        marketE=markets_enum['ftse100'] 
        vi.getNewData(marketE)
        ticker=vi.getTicker("MSFT", marketE)
        #vi.getValueInvestments(ticker, marketE)
        #vi.calculateValueInvestment(marketE)