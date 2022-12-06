import psycopg2
import pandas as pd
import pandas
from DataBaseHelper import DataBaseHelper
import mplfinance as mpf
import pandas as pd
from datetime import date
from marketsenum import markets_enum
from sectorenum import sector_enum
from DataInterfaceHelper import dataInterfaceHelper
from datetime import date, datetime,timedelta

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
        df = pd.DataFrame()
        rlist=[]
        for e in markets_enum.ftse100,markets_enum.ftse250, markets_enum.dow, markets_enum.nasdaq:  
            
            print(df)
            li=self.get_stocks_list(e)
            mdata=di.get_ticker_data(li[0].tickerStrpName)
            mDate=mdata.iloc[-1]['date']
            print(li[0].tickerStrpName +": "+str(mDate))
            rlist.append([e.name,mDate])
            
        df = pd.DataFrame (rlist, columns = ['market', 'last_update'])
        return df
            
        

        
        
suh=StockUpdateHelper()
suh.getMarketStatus()
        
        
        
        