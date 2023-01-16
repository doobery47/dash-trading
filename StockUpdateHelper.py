import psycopg2
import pandas as pd
import pandas
from DataBaseHelper import DataBaseHelper
import pandas as pd
from datetime import date
from marketsenum import markets_enum
from sectorenum import sector_enum
from DataInterfaceHelper import dataInterfaceHelper
from datetime import date, datetime,timedelta
import logging

class StockUpdateHelper(DataBaseHelper):
    def __init__(self):
        DataBaseHelper.__init__(self)
        
    def refineTableData(df):
        if(df.size == 0): # We have an empty table
            startDate = datetime.now() + timedelta(days=-364)
        elif(df.size > 0):
            df2=df.iloc[-1]
            lastDate=df2['date']
        
    def getMarketStatus(self):
        # go through each of the markets and see when 
        # they where last updated
        di = dataInterfaceHelper()
        rlist=[]
        for me in markets_enum:  
            if(me==markets_enum.s_and_p): continue # Ignore S and P for now
            li=self.get_stocks_list(me)
            try:
                mdata=di.get_ticker_data(li[0])
                mDate=mdata.iloc[-1]['date']
                print(li[0].tickerStrpName +": "+str(mDate))
                rlist.append([me.name,mDate])
            except:
                rlist.append([me.name,"undefined"])
            
        df = pd.DataFrame (rlist, columns = ['market', 'last_update'])
        return df
    
    def getTickersMarketStatus(self, marketE):
        # get the list of tickers.
        # go through each one and get the last time it was updated.
        # flag any that not been updated.
        di = dataInterfaceHelper()
        tickers = self.get_stocks_list(marketE)
        rlist=[]
        for ticker in tickers:  
            try:
                print(ticker)
                mdata=di.get_ticker_data(ticker)
                mDate=mdata.iloc[-1]['date']
                print(ticker.tickerStrpName +": "+str(mDate))
                rlist.append([ticker.tickerStrpName,mDate])
            except Exception as e:
                logging.getLogger().error(str(e))
                print(ticker.tickerStrpName+" error")
            
        df = pd.DataFrame (rlist, columns = ['Ticker', 'last_update'])
        return df
        
if __name__ == "__main__":
    suh=StockUpdateHelper()
    # d=suh.getTickersMarketStatus(markets_enum.ftse100)
    # print(d)         
    # suh=StockUpdateHelper()
    # suh.getMarketStatus()
        
        
        
        