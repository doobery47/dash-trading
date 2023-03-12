# functions to either run in issolation clean-up the db or can be called from the main code

from marketsenum import markets_enum
import pandas as pd
from BaseHelper import BaseHelper
from datetime import datetime, timedelta
from DataInterfaceHelper import dataInterfaceHelper
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine



class DB_Maintenance(BaseHelper):
    def __init__(self):
        BaseHelper.__init__(self) 
        
    
    ## to remove coflicts between us and uk table names I will chnage all of the table
    ## names to XX_L
    def ChangeFTSETableNames(self):
        lst=[]
        fl=open("ftse250convert.txt","w")
        for market in ['ftse250']: 
            marketE=markets_enum[market]          
            tickers = self.get_stocks_list(marketE)
            for ticker in tickers:
                tbp=ticker.sqlTickerTableStr.replace("_l","")
                fl.write("ALTER TABLE "+tbp+" RENAME TO "+ticker.sqlTickerTableStr+";\n")
            fl.close()
                    
    
    ###
    ### This was used to cleat up any tables that have null values for the close column.
    ## If a null value is found then we attamot to get a new set of values from Yahoo
    def correctNullCloseValues(self):
        dih = dataInterfaceHelper()
        ## 
        for market in markets_enum:
            if(market.name=='s_and_p' or market.name=='nasdaq'):
                continue
            
            tickers = self.get_stocks_list(market)
            for ticker in tickers:
                tickerHistory=dih.get_historical_data(ticker)
                tickerHistory_new = pd.DataFrame(tickerHistory, columns=['close'])
                # Applying the method
                check_nan = tickerHistory_new['close'].isnull().values.any()
                if(check_nan ==True):
                    print(ticker.tickerStrpName )
                    tickerHistory=dih.get_historical_data(ticker,live=True)
                    if(tickerHistory.empty):
                        continue
                    tickerHistory = tickerHistory.dropna(axis=0, subset=['close'])
                    tickerHistory.to_sql(
                            ticker.sqlTickerTable,
                            con=BaseHelper.conn,
                            schema="public",
                            if_exists="replace",
                            index=False,
                        )
                    BaseHelper.session.commit()
                    
                    
    def removeDuplicateRecords(self):
        dih = dataInterfaceHelper()
        ## 
        for market in markets_enum:
            if(market.name=='s_and_p' or market.name=='nasdaq'):
                continue
            
            tickers = self.get_stocks_list(market)
            for ticker in tickers:
                tickerHistory=dih.get_historical_data(ticker)
                tickerHistory_dup = tickerHistory[tickerHistory.duplicated()]
                #print(tickerHistory_dup.size)
                if(tickerHistory_dup.size >0):
                    print(ticker.tickerStrpName+" has "+str(tickerHistory_dup.size)+" duplicaed records")
                    #tickerHistory.drop_duplicates(subset="date", keep='first', inplace=True)
                    tickerHistory.to_sql(
                            ticker.sqlTickerTable,
                            con=BaseHelper.conn,
                            schema="public",
                            if_exists="replace",
                            index=False,
                        )
                    BaseHelper.session.commit()
                        
    def deleteDuplicateRows(self, marketE):
        tickers = self.get_stocks_list(markets_enum.ftse100)
        for ticker in tickers:
            dth = datetime(2023, 1, 13).date()
            dss = datetime(2023, 1, 16).date()
            BaseHelper.conn.execute(
                "DELETE FROM {} WHERE date = '{}';".format(
                    ticker.sqlTickerTableStr, dth
                )
            )
            BaseHelper.conn.execute(
                "DELETE FROM {} WHERE date = '{}';".format(
                    ticker.sqlTickerTableStr, dss
                )
            )
            BaseHelper.session.commit()

    # def repeat_clean(self):
    #     ftseTickers = self.get_stocks_list(markets_enum.ftse100)
    #     for tickerVals in ftseTickers:
    #        ticker=tickerVals.sqlMarketTableStr
    #        BaseHelper.conn.execute("DELETE FROM {} WHERE rowid > (SELECT MIN(rowid) FROM {} p2 WHERE {}.date = p2.date);".format(ticker,ticker,ticker))
    #        BaseHelper.session.commit()
    
    def sqlachemyTst(self):
        BaseHelper.engine.execute(
            "CREATE TABLE IF NOT EXISTS films (title text, director text, year text)"
        )
        BaseHelper.engine.execute(
            "INSERT INTO films (title, director, year) VALUES ('Doctor Strange', 'Scott Derrickson', '2016')"
        )

        # Read
        result_set = BaseHelper.engine.execute("SELECT * FROM films")
        for r in result_set:
            print(r)

        # Update
        BaseHelper.engine.execute(
            "UPDATE films SET title='Some2016Film' WHERE year='2016'"
        )
        # Delete
        BaseHelper.engine.execute("DELETE FROM films WHERE year='2016'")

    def removeDotL(self):
        df = pd.read_sql_query("SELECT * FROM isa_investments", BaseHelper.conn)
        for rowIndex, row in df.iterrows():
            dd = row["ticker"]
            if row["ticker"] != None:
                newTicker = row["ticker"] + ".L"
                BaseHelper.engine.execute(
                    "UPDATE isa_investments SET ticker='"
                    + newTicker
                    + "' WHERE ticker='"
                    + row["ticker"]
                    + "'"
                )
                BaseHelper.session.commit()

     # This function is used to remove all tables associated with a market.
    # Main reason for this if we find a number of errors in the data then we can
    #clean and start agaim
    # def blatMarkets(self, market):
    #     tickers = self.get_stocks_list(market)
    #     for ticker in tickers:
    #         if sqlalchemy.inspect(self.engine).has_table(ticker.sqlTickerTable):
    #             try:
    #                 DataBaseHelper.engine.execute(
    #                     "DROP TABLE " + ticker.sqlTickerTableStr
    #                 )
    #                 DataBaseHelper.session.commit()
    #                 print(ticker.sqlTickerTableStr+" dropped")
    #                 # ticks = pandas.read_sql_query("SELECT * from "+ticker.sqlTickerTableStr, con=DataBaseHelper.conn)
    #                 # ticks.to_sql(ticker.tickerStrpName, con=DataBaseHelper.conn, if_exists='append',index=False)
    #             except Exception as e:
    #                 print(ticker.sqlTickerTableStr+" NOT dropped")
                    
    # This function is used to determine if we have any missing column names in the value added tables.
    def valueAddedMisingColumnTst(self):
        tstDataFile=open("valueAddedTableData.txt","r")
        line=tstDataFile.read()
        import re
        l = line.split("'")[1::2]; # the [1::2] is a slicing which extracts odd values
        result = [] 
        [result.append(x) for x in l if x not in result] 
        #print(result)
        # print(l)
        # print(l[2]) # to show you how to extract individual items from output
        cf = open("valueAddedColumnNames.txt","r")
        columnNames = cf.read()
        for cName in result:
            if cName not in columnNames:
                print(cName+"\n")
                
 
    # name all tables that have less than 10 records
    def lessThan10Records(self, marketE):
            tickerDel=[]
            tickerTables=[]
            tickers = self.get_stocks_list(marketE)
            for ticker in tickers:
                df = pd.read_sql_query(
                                    "SELECT * FROM {} ;".format(
                                        ticker.sqlTickerTableStr
                                    ),
                                    BaseHelper.conn,
                                )     
                if(df.shape[0] <= 10): 
                    tickerTables.append(ticker.sqlTickerTable)
                    tickerDel.append("DELETE FROM public."+marketE.name+" WHERE epic='"+ticker.ticker+"';")
            print(tickerTables)
            print(tickerDel)
            
    def find8KTables(self):
        lst=["tsibw",
        "gtpbw",
        "bam",
        "efhtu",
        "igacw",
        "fnrg",
        "mnk",
        "hpltw",
        "lase",
        "hlahw",
        "hiiiw",
        "hciiw",
        "hcicw",
        "hcarw",
        "ohpaw",
        "vckaw",
        "gwiiw",
        "gxiiw",
        "sclew",
        "gtpaw",
        "phicw",
        "gsevw",
        "revhw",
        "prme",
        "qomou",
        "svii",
        "gnacw",
        "gmfiw",
        "pticw",
        "laxxw",
        "ndacw",
        "glhaw",
        "giwww",
        "ctm",
        "lmacw",
        "clrmw",
        "giixw",
        "dow",
        "perf",
        "flacw",
        "hudau",
        "mbly",
        "frwaw",
        "agn",
        "rtn",
        "fsrdw",
        "psagw",
        "gsdww",
        "esscr",
        "aqu",
        "esscw",
        "utx",
        "saj",
        "noacw",
        "hcviw",
        "lgcy",
        "aqunu",
        "fssiw",
        "gsrmw",
        "laaaw",
        "xone",
        "swetw",
        "films",
        "glliw",
        "hmcow",
        "afacw",
        "lctx",
        "rca",
        "ec",
        "fei",
        "hypr",
        "apcxw",
        "adnww",
        "etx",
        "agilw",
        "avptw",
        "auudw",
        "avctw",
        "whlrl",
        "aurow",
        "arbew",
        "mggt"]
        for market in markets_enum:
            if(market.name == 'nasdaq' or market.name=='s_and_p'):
                continue
            for tb in lst:
                mar="'"+market.name+"'"
                cmp="'"+tb+"'"
                df = pd.read_sql_query("SELECT * FROM {} ;".format( market.name +" where epic="+cmp), BaseHelper.conn)
                print(df)
                if(df.shape[0]==1):
                    print("delete from "+mar+" where ipic="+cmp)  
            
                    
                              
                
if __name__ == "__main__":
    dbm =DB_Maintenance()
    nasLst=["ftse100", "ftse250", "dow"]

    dbm.find8KTables()