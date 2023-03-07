# https://quantpy.com.au/python-for-finance/warren-buffett-value-investing-like-a-quant/


from BaseHelper import BaseHelper
import concurrent.futures as cf
from yahoofinancials import YahooFinancials
import time
from marketsenum import markets_enum
import pandas as pd
import logging
import pandas
from GraphHelper import GraphHelper
from DataInterfaceHelper import dataInterfaceHelper
from datetime import datetime, timedelta

import collections


class ValueInvestingHelper(BaseHelper):
    def __init__(self):
        BaseHelper.__init__(self)

    dih = dataInterfaceHelper()
    gh = GraphHelper()
    
    
    roe_dict, epsg_dict = {}, {}
    

    balanceSheet = {}
    incomeStatement = {}
    cashStatement = {}
    
    # def getGraphFig(self,ticker):

    #     data = self.dih.get_historical_data(
    #         ticker, datetime.now() + timedelta(days=-364), False
    #     )
    #     return self.gh.getGraph(data, ticker, "£")
    

    def retrieve_stock_data(self, stock):
        try:
            print(stock.ticker)
            tstFile=open("valueTst.txt","a")
            tstFile.write(stock.ticker)
            yahoo_financials = YahooFinancials(stock.tickerYahoo)
            balance_sheet_data = yahoo_financials.get_financial_stmts("annual", "balance")
            print(balance_sheet_data)
            income_statement_data = yahoo_financials.get_financial_stmts("annual", "income")
            print(income_statement_data)
            # cash_statement_data = yahoo_financials.get_financial_stmts(
            #     "annual", "cash")
            # print(cash_statement_data)
            self.balanceSheet[stock.ticker] = balance_sheet_data["balanceSheetHistory"][
                stock.tickerYahoo
            ]
            self.incomeStatement[stock.ticker] = income_statement_data[
                "incomeStatementHistory"
            ][stock.tickerYahoo]
            # self.cashStatement[stock.ticker] = cash_statement_data[
            #     "cashflowStatementHistory"
            # ][stock.tickerYahoo]
        except Exception as e:
            print("error with retrieving stock data :" + e+" stock: "+stock)

    def financialInfo(self, marketE):
        print(marketE.name)
        stocks = []
        stocks = self.get_stocks_list(marketE)

        start = time.time()
        executor = cf.ThreadPoolExecutor(3)
        futures = [executor.submit(self.retrieve_stock_data, stock) for stock in stocks]
        cf.wait(futures)
        end = time.time()

        self.__sheetConversion(self.balanceSheet, "val_inv_anal_balsheet",marketE)
        self.__sheetConversion(self.incomeStatement, "val_inv_anal_incomesheet",marketE)
        #self.__sheetConversion(self.cashStatement, "val_inv_anal_cashsheet",marketE)

        print("  time taken {:.2f} s".format(end - start))

    def __sheetConversion(self, sheetData, sheetTableExt,marketE):
        
        # remove the old records first
        self.engine.execute("DELETE FROM "+sheetTableExt+" WHERE market='"+marketE.name+"'")
        BaseHelper.session.commit()


        for ticker in sheetData:
            if sheetData[ticker] == None:
                continue

            for bs in sheetData[ticker]:
                print(bs)
                theDate = ""
                for key, value in bs.items():
                    theDate = key
                df = pd.DataFrame.from_dict(bs, orient="index")
                df["date"] = theDate
                df.rename(columns={list(df)[0]: "date"}, inplace=True)
                df['market']=marketE.name
                df["epic"] = ticker.lower()
                # A lot of column names in yahoo history have changed but we only need the ones below
                # So we will save these and ignore the rest. 
                # Improvement. We get all of the data, build the dataframe and remove the columns that are not required.
                # Should just extract the columns we need and then build the table.
                if(sheetTableExt == 'val_inv_anal_balsheet'): 
                    df.drop(df.columns.difference(['date','market', 'epic', 'stockholdersEquity', 'commonStock']), 1, inplace=True)
                else:
                    df.drop(df.columns.difference(['date','market', 'epic', 'grossProfit','netIncome']), 1, inplace=True)
                print(df)
                df.to_csv("valueTst.csv")

                try:
                    df.to_sql(
                        sheetTableExt,
                        con=BaseHelper.engine,
                        if_exists="append",
                        index=False,
                    )
                    BaseHelper.session.commit()
                except Exception as e:
                    logging.getLogger().debug(str(e))

    def finalResults(self):
        ROE_req = 10
        EPSG_req = 10
        print("-" * 50, "RETURN ON EQUITY", "-" * 50)
        roe_crit = {
            k: v
            for (k, v) in self.roe_dict.items()
            if v[0] >= ROE_req and sum(n < 0 for n in v[1]) == 0
        }
        print(roe_crit)
        print("-" * 50, "EARNINGS PER SHARE GROWTH", "-" * 50)
        eps_crit = {
            k: v
            for (k, v) in self.epsg_dict.items()
            if v[0] >= EPSG_req and sum(n < 0 for n in v[1]) == 0
        }
        print(eps_crit)
        print("-" * 50, "ROE & EPS Growth Critera", "-" * 50)
        both = [
            key1 for key1 in roe_crit.keys() for key2 in eps_crit.keys() if key2 == key1
        ]
        print(both)
        return both
    
    def processDataForMarket(self, marketE):
        tickers = self.get_stocks_list(marketE)
        return self.processDataForTickers(tickers, marketE)
    
    def processDataForTickers(self, tickers, marketE):   
        self.epsg_dict, self.roe_dict = {}, {}
        count_missing, count_cond, count_eps_0 = 0, 0, 0
        for ticker in tickers:
            try:
                lTicker = ticker.ticker.lower()
                balSql = "SELECT * FROM public.val_inv_anal_balsheet where market='"+ marketE.name+ "' AND epic='"+ lTicker+ "';"
                balanceSheets = pandas.read_sql_query(
                    "SELECT * FROM public.val_inv_anal_balsheet where market='"
                    + marketE.name
                    + "' AND epic='"
                    + lTicker
                    + "';",
                    con=BaseHelper.conn,
                )
                balSql = "SELECT * FROM public.val_inv_anal_incomesheet where market='"+ marketE.name+ "' AND epic='"+ lTicker+ "';"
                incomeSheets = pandas.read_sql_query(
                    "SELECT * FROM public.val_inv_anal_incomesheet where market='"
                    + marketE.name
                    + "' AND epic='"
                    + lTicker
                    + "';",
                    con=BaseHelper.conn,
                )
                
                # balSheetsDates = balanceSheets["date"].to_list()
                # incomeSheetsDates = incomeSheets["date"].to_list()
                
                #we need to get 2 lists that have the same dates.
                allDate=balanceSheets["date"].to_list()+incomeSheets["date"].to_list()
                dates=[item for item, count in collections.Counter(allDate).items() if count > 1]

 
                if len(allDate) >=2:
                    count_cond += 1
                    
                    equity = balanceSheets[balanceSheets['date'].isin(dates)]["stockholdersEquity"].to_list()
                    commonStock = balanceSheets[balanceSheets['date'].isin(dates)]["commonStock"].to_list()
                    profit = incomeSheets[incomeSheets['date'].isin(dates)]["grossProfit"].to_list()
                    netIncome = incomeSheets[incomeSheets['date'].isin(dates)]["netIncome"].to_list()

                    # equity = balanceSheets["stockholdersEquity"].to_list() # used to be called "totalStockholderEquity"
                    # commonStock = balanceSheets["commonStock"].to_list()
                    # profit = incomeSheets["grossProfit"].to_list()
                    # revenue = incomeSheets["totalRevenue"].to_list()
                    # netIncome = incomeSheets["netIncome"].to_list()
                    roe = [
                        round(netin / equity * 100, 2)
                        for netin, equity in zip(netIncome, equity)
                    ]  # per year
                    self.roe_dict[lTicker] = (round(sum(roe) / len(roe), 2), roe)
                    eps = [
                        round(earn / stono, 2)
                        for earn, stono in zip(profit, commonStock)
                    ]  # per year

                    try:
                        epsg = []
                        for ep in range(len(eps)):
                            if ep == 0:
                                continue
                            elif ep == 1:
                                epsg.append(
                                    round(100 * ((eps[ep - 1] / eps[ep]) - 1), 2)
                                )
                            elif ep == 2:
                                epsg.append(
                                    round(
                                        100 * ((eps[ep - 2] / eps[ep]) ** (1 / 2) - 1),
                                        2,
                                    )
                                )
                                epsg.append(
                                    round(100 * ((eps[ep - 1] / eps[ep]) - 1), 2)
                                )
                            elif ep == 3:
                                epsg.append(
                                    round(
                                        100 * ((eps[ep - 3] / eps[ep]) ** (1 / 3) - 1),
                                        2,
                                    )
                                )
                                epsg.append(
                                    round(100 * ((eps[ep - 1] / eps[ep]) - 1), 2)
                                )
                            else:
                                print("More than 4 years of FY data")
                        self.epsg_dict[lTicker] = (
                            round(sum(epsg) / len(epsg), 2),
                            epsg,
                        )
                    except:
                        count_eps_0 += 1
                        self.epsg_dict[lTicker] = (0, eps)
            except:
                count_missing += 1

        print("Yearly data avail", count_cond, "out of", len(self.balanceSheet))
        print("Some key data missing", count_missing, "out of", len(self.balanceSheet))
        print("EPS Growth NaN", count_eps_0, "out of", len(self.balanceSheet))

    def getTableStatusData(self):
        # go through val_inv_anal_balsheet and get the last time each of the marketss where updated
        # create dictionary and return to be displayed in a table
        rList=[]
        
        for market in markets_enum:
            if(market.name=='s_and_p' or market.name=='nasdaq'):
                continue
            
            df = pd.read_sql_query("SELECT * FROM public.val_inv_anal_balsheet where market='{}' ORDER BY date desc limit 1".format(
                                                                                 market.name), BaseHelper.conn)
            if(df.empty):
                mDate="Unknown"
            else:
                mDate=df.iloc[-1]['date']
            rList.append([market.name,mDate])
            
        return pd.DataFrame (rList, columns = ['market', 'last_update'])
        
        

if __name__ == "__main__":
    vih = ValueInvestingHelper()
    # vih.financialInfo(markets_enum.dow)
    # vih.processData(markets_enum.ftse100)
    #vih.deleteRows()

    # vih.finalResults()
    # ttv=TickerTypeVals("","","","ABDN","ABDN.L")
    # ttv.tickerYahoo="ABDN.L"
    # ttv.tickerStrpName="ABDN"
    # vih.getTickerData(ttv, markets_enum.ftse100)
    
    vih.getTableStatusData()
