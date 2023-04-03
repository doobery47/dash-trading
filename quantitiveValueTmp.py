from yahoofinancials import YahooFinancials
import yahoo_fin.stock_info as si
import pandas as pd
import psycopg2
import pandas as pd
import pandas
from BaseHelper import BaseHelper
import pandas as pd
from datetime import date
from marketsenum import markets_enum
from sectorenum import sector_enum
from DataInterfaceHelper import dataInterfaceHelper
from datetime import date, datetime,timedelta
import logging

class quantitiveValueTest(BaseHelper):
    def __init__(self):
        BaseHelper.__init__(self)
    def largeValConversion(self, x):
            print(x)
            if not x:
                return ""
            elif x=='nan' or pd.isna(x):
                return '0'
            
            try:
                if x.endswith('T'):
                    return str(float(x.replace('T',''))*1000000000000000000)
                elif x.endswith("B"):
                    return float(x.replace('B',''))*1000000000
                elif x.endswith('M'):
                    return float(x.replace('M',''))*1000000
                elif x.endswith('k'):
                    return float(x.replace('k',''))*1000
                else:
                    return x
            except Exception as e:
                print(e)

    yahoo_financials = YahooFinancials("msft")
    # outstandingShares = aapl.info['sharesOutstanding']
    # print(outstandingShares)
    # cash_statement_data = yahoo_financials.get_financial_stmts("annual", "cash")
    # print(cash_statement_data)

    tickers=['GS','HD','MSFT','MCD','AMGN','V','HON','CRM','CAT','JNJ','BA','AAPL','TRV','AXP',
            'CVX','PG','MMM','IBM','WMT','NKE',
            'JPM','DIS','MRK','KO','CSCO','VZ','WBA','INTC']
    
    def __getCashFlow(self, ticker, marketE):
        ss="SELECT * FROM ratio_cash where epic="+ticker.sqlMarketTableStr+"and market='"+marketE.name+"'  ORDER BY date"
        df = pd.read_sql_query("SELECT * FROM ratio_cash where epic="+ticker.sqlMarketTableStr+"and market='"+marketE.name+"' ORDER BY date", BaseHelper.conn)   # type: ignore
        # Clean Data. remove cash flow that has a null value and if we have 5 dates remove the 
        allDates=df["date"].to_list()
        df1=df.dropna() # remove any free cahs flows that no value
        #print(df1)
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
    
    def test(self):
        marketE=markets_enum['dow'] 

        for ticker in self.tickers:
            data=si.get_stats(ticker)
            data['Value'] = data['Value'].astype(str)
            #print(data)
            # data['Value'] = data['Value'].map(lambda x: x.rstrip('%'))
            # data['Value'] = data['Value'].map(lambda x: str(self.__largeValConversion(x))  )
            data.index=data["Attribute"]
            data=data.drop(labels="Attribute",axis=1)
            raw_table=data.T
            #print(raw_table)
            outstandingShares=raw_table['Shares Outstanding 5']
            outstandingShares=self.largeValConversion(raw_table.iloc[0]['Shares Outstanding 5'])

            required_rate=0.07
            perptual_rate=0.02
            cashflowgrowthrate=0.03

            years=[1,2,3,4]

            #freecashflow=[50803000, 64121000, 58896000, 73365000]
            tick = self.getTicker(ticker, marketE)
            freecashflow = self.__getCashFlow(tick, marketE)

            futurefreecashflow=[]
            discountfactor=[]
            discountedfuturefreecashflow=[]

            terminalvalue=freecashflow[-1]*(1+perptual_rate)/(required_rate-perptual_rate)

            #print(terminalvalue)

            for year in years:
                cashflow=freecashflow[-1]*(1+cashflowgrowthrate)**year
                futurefreecashflow.append(cashflow)
                discountfactor.append((1+required_rate)**year)
                
            #print(futurefreecashflow)
            #print(discountfactor)

            for i in range(0, len(years)):
                discountedfuturefreecashflow.append(futurefreecashflow[i]/discountfactor[i])
                
            #print(discountedfuturefreecashflow)

            dicsountterminalvalue=terminalvalue/(1+required_rate)**4
            discountedfuturefreecashflow.append(dicsountterminalvalue)

            todaysvalue=sum(discountedfuturefreecashflow)

            fairvalue=todaysvalue*1000/outstandingShares
            print(ticker+": "+str(fairvalue))
            
        
if __name__ == "__main__":
    tst = quantitiveValueTest()
    tst.test()
