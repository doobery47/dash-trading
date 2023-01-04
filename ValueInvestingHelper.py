#https://quantpy.com.au/python-for-finance/warren-buffett-value-investing-like-a-quant/
#https://docs.streamlit.io/knowledge-base/using-streamlit/hide-row-indices-displaying-dataframe

from DataBaseHelper import DataBaseHelper
import concurrent.futures as cf
from yahoofinancials import YahooFinancials
import ast
import time
import os
from marketsenum import markets_enum
import pandas as pd
import logging
import pandas



class ValueInvestingHelper(DataBaseHelper):
    def __init__(self):
        DataBaseHelper.__init__(self)
        
    roe_dict, epsg_dict = {}, {}
    
    balanceSheet = {}
    incomeStatement = {}
    cashStatement = {}
    
    def retrieve_stock_data(self, stock):
        try:
            print(stock)
            yahoo_financials = YahooFinancials(stock.tickerYahoo)
            balance_sheet_data = yahoo_financials.get_financial_stmts('annual', 'balance')
            print(balance_sheet_data)
            income_statement_data = yahoo_financials.get_financial_stmts('annual', 'income')
            print(income_statement_data)
            cash_statement_data = yahoo_financials.get_financial_stmts('annual', 'cash')
            print(cash_statement_data)
            self.balanceSheet[stock.ticker] = balance_sheet_data['balanceSheetHistory'][stock.tickerYahoo]
            self.incomeStatement[stock.ticker] = income_statement_data['incomeStatementHistory'][stock.tickerYahoo]
            self.cashStatement[stock.ticker] = cash_statement_data['cashflowStatementHistory'][stock.tickerYahoo]
        except Exception as e:
            print('error with retrieving stock data :'+e)
            
    def financialInfo(self, marketE):
        print(marketE.name)
        stocks = []
        stocks = self.get_stocks_list(marketE)
        
        start = time.time()
        executor = cf.ThreadPoolExecutor(3)
        futures = [executor.submit(self.retrieve_stock_data, stock) for stock in stocks]
        cf.wait(futures)
        end = time.time()
        
        self.sheetConversion(self.balanceSheet, "val_inv_anal_balanceSheet")
        self.sheetConversion(self.incomeStatement, "val_inv_anal_incomeStatement")
        self.sheetConversion(self.cashStatement, "val_inv_anal_cashStatement.txt")
        
        print('  time taken {:.2f} s'.format(end-start))
        
    def sheetConversion(self, sheetData, sheetTableExt):
 
        for ticker in sheetData:
            self.createBalanceSheetTable(ticker.lower())
            if(sheetData[ticker] == None):
                continue

            for bs in sheetData[ticker]:
                theDate = ""
                for key, value in bs.items():
                    theDate = key
                df=pd.DataFrame.from_dict(bs, orient='index')               
                df['date']=theDate
                df.rename(columns = {list(df)[0]: 'date'}, inplace = True)
                try:
                    df.to_sql(ticker.lower()+"_balsheet", con=DataBaseHelper.engine, if_exists='append',index=False) 
                    DataBaseHelper.session.commit()
                except Exception as e:
                    logging.getLogger().debug(str(e))
            print(ticker+sheetTableExt+" table create")
        
    def finalResults(self):
        ROE_req = 10
        EPSG_req = 10
        print('-'*50, 'RETURN ON EQUITY','-'*50)
        roe_crit = {k:v for (k,v) in self.roe_dict.items() if v[0] >= ROE_req and sum(n < 0 for n in v[1])==0}
        print(roe_crit)
        print('-'*50, 'EARNINGS PER SHARE GROWTH','-'*50)
        eps_crit = {k:v for (k,v) in self.epsg_dict.items() if v[0] >= EPSG_req and sum(n < 0 for n in v[1])==0}
        print(eps_crit)
        print('-'*50, 'ROE & EPS Growth Critera','-'*50)
        both = [key1 for key1 in roe_crit.keys() for key2 in eps_crit.keys() if key2==key1]
        print(both)
        return both
        
    def processData(self, marketE):
        
        with open('analysis_data/'+marketE.name+'_balanceSheet.txt', 'r') as input: # dict off tickers wicth contain a dict of date and data
            balanceSheet = ast.literal_eval(input.read())
        with open('analysis_data/'+marketE.name+'_incomeStatement.txt', 'r') as input:
            incomeStatement = ast.literal_eval(input.read())
                    
        count_missing, count_cond, count_eps_0 = 0, 0, 0
        tickers = self.get_stocks_list(marketE)
        for ticker in tickers:
            try:
                lTicker=ticker.ticker.lower()
                balanceSheets = pandas.read_sql_query("SELECT * FROM public.val_inv_anal_balsheet where market='"+marketE.name+"' AND epic='"+lTicker+"';", 
                                                    con=DataBaseHelper.conn)
                incomeSheets = pandas.read_sql_query("SELECT * FROM public.val_inv_anal_incomesheet where market='"+marketE.name+"' AND epic='"+lTicker+"';", 
                                                    con=DataBaseHelper.conn)
                
                balSheetsDates = balanceSheets['date'].to_list()
                incomeSheetsDates = incomeSheets['date'].to_list()
                if balSheetsDates == incomeSheetsDates:
                    count_cond += 1
                
                    equity=balanceSheets['totalStockholderEquity'].to_list()
                    commonStock=balanceSheets['commonStock'].to_list()
                    profit=incomeSheets['grossProfit'].to_list()
                    revenue=incomeSheets['totalRevenue'].to_list()
                    netIncome=incomeSheets['netIncome'].to_list()
                    roe = [round(netin/equity*100,2) for netin, equity in zip(netIncome, equity)] # per year
                    self.roe_dict[lTicker] = (round(sum(roe)/len(roe),2), roe)
                    eps = [round(earn/stono,2) for earn, stono in zip(profit, commonStock)] # per year
                                        
                    try:
                        epsg = []
                        for ep in range(len(eps)):
                            if ep == 0:
                                continue
                            elif ep == 1:
                                epsg.append(round(100*((eps[ep-1]/eps[ep])-1),2))
                            elif ep == 2:
                                    epsg.append(round(100*((eps[ep-2]/eps[ep])**(1/2)-1),2))
                                    epsg.append(round(100*((eps[ep-1]/eps[ep])-1),2))
                            elif ep == 3:
                                epsg.append(round(100*((eps[ep-3]/eps[ep])**(1/3)-1),2))
                                epsg.append(round(100*((eps[ep-1]/eps[ep])-1),2))
                            else:
                                print('More than 4 years of FY data')  
                        self.epsg_dict[lTicker] = (round(sum(epsg)/len(epsg),2), epsg)
                    except:
                        count_eps_0 += 1
                        self.epsg_dict[lTicker] = (0, eps)
            except  :
                count_missing += 1
        
                
        print('Yearly data avail',count_cond, 'out of', len(self.balanceSheet))
        print('Some key data missing', count_missing, 'out of', len(self.balanceSheet))
        print('EPS Growth NaN', count_eps_0, 'out of', len(self.balanceSheet))


      
if __name__ == "__main__":
    vih = ValueInvestingHelper() 
    vih.financialInfo(markets_enum.dow) 
    vih.processData(markets_enum.ftse100)

    #vih.finalResults()  
    #ttv=TickerTypeVals("","","","ABDN","ABDN.L")
    # ttv.tickerYahoo="ABDN.L"
    # ttv.tickerStrpName="ABDN"
    #vih.getTickerData(ttv, markets_enum.ftse100)        

