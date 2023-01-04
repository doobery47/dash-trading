from marketsenum import markets_enum
from sectorenum import sector_enum
import pandas as pd
import pandas_datareader as pdr
from DataBaseHelper import DataBaseHelper
from datetime import date, datetime,timedelta
import yfinance as yf
from industries import ind,sector
import pandas
import logging


class dataInterfaceHelper(DataBaseHelper):
    FTSE100="https://www.marketwatch.com/investing/index/ukx/downloaddatapartial?startdate={}&enddate={}&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false&countrycode=uk"
    FTSE250="https://www.marketwatch.com/investing/index/mcx/downloaddatapartial?startdate={}&enddate={}&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false&countrycode=uk"
    DowJones="https://www.marketwatch.com/investing/index/djia/downloaddatapartial?startdate={}&enddate={}&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false"
    NASDAQ="https://www.marketwatch.com/investing/index/comp/downloaddatapartial?startdate={}&enddate={}&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false"
    S_AND_P="https://www.marketwatch.com/investing/index/spx/downloaddatapartial?startdate={}&enddate={}&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false"

    marketDict = {markets_enum.ftse100.name: FTSE100, markets_enum.ftse250.name: FTSE250,markets_enum.dow.name:DowJones,
              markets_enum.nasdaq.name:NASDAQ, markets_enum.s_and_p.name:S_AND_P}
    
    def __init__(self):
        DataBaseHelper.__init__(self)
        
    def get_marketData(self, marketsE, period='year to date', sec=sector_enum.none):
        tableName = marketsE.name+"_historic_values"
        if(period == 'year to date'):  
            startDate = (datetime.now() + timedelta(days=-364)).date() 
            if(sec != sector_enum.none and marketsE == markets_enum.nasdaq):
                  df = pd.read_sql_query("SELECT * from {} WHERE sector='{}' and \"date\" > '{}'::date".format(tableName, self.getSectorStringVal(sec),startDate), 
                                   DataBaseHelper.conn)
            else:
                df = pd.read_sql_query("SELECT * from {} WHERE \"date\" > '{}'::date".format(tableName, startDate), 
                                   DataBaseHelper.conn)
        else:
            if(sec != sector_enum.none and marketsE == markets_enum.nasdaq):
                  df = pd.read_sql_query("SELECT * from {} WHERE sector='{}'".format(tableName, self.getSectorStringVal(sec)), 
                                   DataBaseHelper.conn)
            else:
                df = pd.read_sql_query("SELECT * FROM {} ;".format(tableName), DataBaseHelper.conn)


        for i in (df.columns):
            if(i=='date'):
                continue
            df[i] = df[i].astype(float)
        
        df.index = pd.to_datetime(df.date)       
        df=df.sort_index()
        return df
        
    def get_ticker_data(self, ticker):
        ticker=self.mod_table_digit_name(ticker)
        #ticker="\""+ticker+"\""
        df = pd.read_sql_query("SELECT * FROM public."+ticker,DataBaseHelper.conn)
        return df
    
    def get_historical_data(self, symbol, start_date = None, live=False):
        
        df=None
        if(live):
            tickerData = yf.Ticker(symbol.tickerYahoo)
            delta = datetime.now() -datetime.strptime(start_date, '%Y-%m-%d')
            df = tickerData.history(period=str(delta.days)+'d')
            df = df.drop('Dividends', axis=1)
            df = df.drop('Stock Splits', axis=1)
            #df = pdr.get_data_yahoo(symbol.tickerYahoo, start=start_date, end=datetime.now())
            df.rename(columns={'Open':'open', 'Close':'close', 'High':'high', 'Low':'low', 'Volume':'volume', 'Date':'date'}, inplace=True)
            for i in df.columns:
                df[i] = df[i].astype(float)
        else:
            df = pd.read_sql_query("SELECT * FROM "+symbol.sqlTickerTableStr, DataBaseHelper.conn)
            for i in (df.columns):
                if(i=='date'):
                    continue
                df[i] = df[i].astype(float)
            df.index = pd.to_datetime(df.date)
            #start_date = None
            if start_date:
                df = df[df.index >= start_date]

        df.index = pd.to_datetime(df.index)
        if start_date:
            df = df[df.index >= start_date]
        return df
      
    def UpdateMarketData(self, marketsE, sec=sector_enum.none):
        df = self.get_marketData(marketsE, sec)        
        df['date'] = pd.to_datetime(df['date'])
        if(df.size == 0): # We have an empty table
            startDate = datetime.now() + timedelta(days=-364)
        elif(df.size > 0):
            df2=df.iloc[-1]
            lastDate=df2['date']
            startDate=(pd.to_datetime(lastDate) + pd.DateOffset(days=1)).date()       
            if(startDate >= date.today()):#- timedelta(days=1)):
                print("Wont process "+marketsE.name+" as end date is equal to or greater than today")
                return
        
        startDateStr=startDate.strftime("%m/%d/%Y")
        endDateStr=datetime.now().strftime("%m/%d/%Y")
        marketStr = self.marketDict[marketsE.name]
        market=marketStr.format(startDateStr,endDateStr)
        
        df= pd.read_csv(market)
        print(df)
        df.rename(columns={'Open':'open', 'Close':'close', 'High':'high', 'Low':'low', 'Volume':'volume', 'Date':'date'}, inplace=True)
        df['close'] = df['close'].str.replace('\,', '',regex=True)
        df['open'] = df['open'].str.replace('\,', '', regex=True)
        df['high'] = df['high'].str.replace('\,', '', regex=True)
        df['low'] = df['low'].str.replace('\,', '', regex=True)
        df['date'] = pd.to_datetime(df['date'])
        df.to_sql(marketsE.name+"_historic_values", con=DataBaseHelper.engine, if_exists='append',index=False)    
        DataBaseHelper.session.commit()
        
    def updateHistoryDataForTicker(self, tickerNameContainer):                                
            #get last record and date form table
            sql = """INSERT INTO ticket_errors(epic, name, reason, timestamp) VALUES(%s,%s,%s,%s);"""
        
            startDate=datetime.strptime('2017-07-30','%Y-%m-%d').date()
            try: 
                if self.tableExists(tickerNameContainer.sqlTickerTableStr.lower()):             
                    df_db = pd.read_sql_query('SELECT * FROM "{}" ORDER BY date DESC LIMIT 1;'.format(tickerNameContainer.sqlTickerTableStr.lower()), DataBaseHelper.conn)
                    startDate=(pd.to_datetime(df_db['date'][0]) + pd.DateOffset(days=1)).date()
                    if(startDate >= date.today()):
                        status="Wont process "+tickerNameContainer.tickerStrpName+" as end date is equal to or greater than today"
                        return status
                else: # no table found so we will create one and set up some default data
                    self.createTable(tickerNameContainer.sqlTickerTableStr.lower())
            except Exception as e: ## report the problem and remove entr from tickerr table
                logging.getLogger().error(str(e))
                raise e
    
            try:
                tickerData = yf.Ticker(tickerNameContainer.tickerYahoo)
                delta = date.today()-startDate
                df = tickerData.history(period=str(delta.days)+'d')
                df = df.drop('Dividends', axis=1)
                df = df.drop('Stock Splits', axis=1)
                #df = pdr.get_data_yahoo(tickerNameContainer.tickerYahoo, startDate, date.today())
                df.to_csv ('test.csv')
                data = pd.read_csv("test.csv")
                print(data)
                print("processed: "+tickerNameContainer.tickerStrpName)
            except Exception as e:
                logging.getLogger().error(str(e))
                # DataBaseHelper.conn.execute(sql, (tickerNameContainer.tickerStrpName,tickerNameContainer.tickerStrpName,str(e),date.today().strftime('%Y-%m-%d'),))
                # DataBaseHelper.session.commit()
                raise e   
            
            data.rename(columns={'Open':'open', 'Close':'close', 'High':'high', 'Low':'low', 'Volume':'volume', 'Date':'date'}, inplace=True)
            data.date = pd.to_datetime(data.date)
            # need to set table name to lower as panda puts name in double quotes as we need a lower case name    
            data.to_sql(tickerNameContainer.sqlTickerTableStr.lower(), con=DataBaseHelper.conn, 
                         schema='public', if_exists='append',index=False)
                
            DataBaseHelper.session.commit()           
            return "Complete"
        
        
    def getTickerDataTest(self, ttv, marketE):
        # pandas display options
        pd.set_option('display.max_colwidth', -1)

        sector="financial"
        longBusinessSummary="s simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book."
        grossProfits=2938000000
        profitMargins=0.13743
        totalCash=970000000
        totalDebt=4012999936
        forwardEps=0.18
        bookValue=0.909
        forwardPE=7.5444446
        longName=ttv.ticker+" bla bla bla"
        companyURL="https://www.bbc.co.uk/news"
        companyURL = f'<a target="_blank" href="{companyURL}">Company URL</a>'
        if(grossProfits >1000000):
            grossProfits = str(round(grossProfits/1000000,2))+"m"
            totalCash = str(round(totalCash/1000000,2))+"m"
            totalDebt = str(round(totalDebt/1000000,2))+"m"
                 
        data = [['sector', sector], 
               # ['long Business Summary', longBusinessSummary],
                ['gross Profits', grossProfits],
                ['profit Margins',profitMargins],
                ['total Cash',totalCash],
                ['total Debt',totalDebt],
                ['forward Eps',forwardEps],
                ['book Value',bookValue],
                ['forward PE',forwardPE],
                ['long Name',longName],
                ['company URL', companyURL]]
  
        # Create the pandas DataFrame
        df = pd.DataFrame(data, columns=['Name', 'Description'])
        df = df.to_html(escape=False)
        return df
        
    def getTickerData(self, ttv, marketE):
        pd.set_option('display.max_colwidth', -1)
        stock = yf.Ticker(ttv.tickerYahoo)
        dict =  stock.info
        sector=dict["sector"]
        grossProfits=dict["grossProfits"]
        profitMargins=dict["profitMargins"]
        totalCash=dict["totalCash"]
        totalDebt=dict["totalDebt"]
        forwardEps=dict["forwardEps"]
        bookValue=dict["bookValue"]
        forwardPE=dict["forwardPE"]
        website=dict['website']
        currentPrice=dict['currentPrice']
        previousClose=dict['previousClose']
        priceToBook=dict['priceToBook']
        website = f'<a target="_blank" href="{website}">Company URL</a>'
        increase=round(100*(float(currentPrice)-float(previousClose))/float(previousClose),3)
        
        if(grossProfits >1000000):
            grossProfits = str(round(grossProfits/1000000,2))+"m"
            totalCash = str(round(totalCash/1000000,2))+"m"
            totalDebt = str(round(totalDebt/1000000,2))+"m"
        
        data = [['sector', sector], 
                ['current price', currentPrice],
                ['previous close',previousClose],
                ['increase',str(increase)+"%"],
                ['gross profits', grossProfits],
                ['profit margins',profitMargins],
                ['total cash',totalCash],
                ['total debt',totalDebt],
                ['forward EPS',forwardEps],
                ['book value',bookValue],
                ['price to book',priceToBook],
                ['forward PE',forwardPE],
                ['website',website]]
  
        # Create the pandas DataFrame
        df = pd.DataFrame(data, columns=['Name', 'Description'])
        #df = df.to_html(escape=False)
        return df
            
    def repeat_clean(self):
        ftseTickers = self.get_stocks_list(markets_enum.ftse100)
        for tickerVals in ftseTickers:
           ticker=tickerVals.sqlMarketTableStr
           DataBaseHelper.conn.execute("DELETE FROM {} WHERE rowid > (SELECT MIN(rowid) FROM {} p2 WHERE {}.date = p2.date);".format(ticker,ticker,ticker))
           DataBaseHelper.session.commit()

    def sqlachemyTst(self):
        DataBaseHelper.engine.execute("CREATE TABLE IF NOT EXISTS films (title text, director text, year text)")  
        DataBaseHelper.engine.execute("INSERT INTO films (title, director, year) VALUES ('Doctor Strange', 'Scott Derrickson', '2016')")

        # Read
        result_set = DataBaseHelper.engine.execute("SELECT * FROM films")  
        for r in result_set:  
            print(r)

        # Update
        DataBaseHelper.engine.execute("UPDATE films SET title='Some2016Film' WHERE year='2016'")
        # Delete
        DataBaseHelper.engine.execute("DELETE FROM films WHERE year='2016'")  
        
    def removeDotL(self):
        df = pd.read_sql_query("SELECT * FROM isa_investments", DataBaseHelper.conn)
        for rowIndex, row in df.iterrows():
            dd=row['ticker']
            if(row['ticker'] != None):
                newTicker=row['ticker']+".L"
                DataBaseHelper.engine.execute("UPDATE isa_investments SET ticker='"+newTicker+"' WHERE ticker='"+row['ticker']+"'")
                DataBaseHelper.session.commit()
                
    def getMarketCurrentValue(self, marketE):
        marketStr=""
        if(marketE == markets_enum.ftse100):
            marketStr='^FTSE'
        elif(marketE == markets_enum.ftse250):
            marketStr='^FTMC'
        elif(marketE == markets_enum.dow): 
            marketStr='^DJI' 
        elif(marketE == markets_enum.nasdaq): 
            marketStr='NQ=F'
        elif(marketE == markets_enum.s_and_p): 
            marketStr='^GSPC'
        ticker = yf.Ticker(marketStr).info
        return ticker['regularMarketPrice'], ticker['previousClose']
    
    def tableBuilder(self):
        # select each industry in turn.
        # create a table
        # get the values from the nasdaq table
        # add these rows into the created table
        
        f=open("nasdaqSort.txt","w")
        for i in sector:
            ticks = pandas.read_sql_query("SELECT epic,name,ipo_year,sector,country,industry,last_update from nasdaq WHERE sector='"+i+"'", 
                                                 con=DataBaseHelper.conn)
            ticks.to_sql("nasdaq_"+i, con=DataBaseHelper.conn, if_exists='append',index=False)
            DataBaseHelper.session.commit()
            # for tick in ticks.iterrows():
            #     print(tick)
            #f.write(ticks.to_string()+" : "+count(ticks)+i+"\n")
            print(ticks)
        f.close()
        
    def removeLastRecFromTable(self,marketE):
        tickers = self.get_stocks_list(marketE)
        for ticker in tickers:
            lTicker=ticker.sqlTickerTableStr.lower()
            try:
                DataBaseHelper.conn.execute('DELETE FROM "'+lTicker+'" WHERE date in(SELECT MAX("date") FROM "'+lTicker+'") ')
            except Exception as e:
                print(e)
           
            
    
if __name__ == "__main__":    
    # handler = logging.FileHandler('app.log')
    # handler.setLevel(logging.DEBUG)
    # logging.getLogger('sqlalchemy').addHandler(handler)
    # db_log_file_name = 'db.log2'
    # db_handler_log_level = logging.INFO
    # db_logger_log_level = logging.DEBUG

    # db_handler = logging.FileHandler(db_log_file_name)
    # db_handler.setLevel(db_handler_log_level)

    # db_logger = logging.getLogger('sqlalchemy')
    # db_logger.addHandler(db_handler)
    # db_logger.setLevel(db_logger_log_level)
    
    tst=dataInterfaceHelper()
    tst.removeLastRecFromTable(markets_enum.ftse100)
    tst.removeLastRecFromTable(markets_enum.dow)
    tst.removeLastRecFromTable(markets_enum.nasdaq_BasicMaterials)
    tst.removeLastRecFromTable(markets_enum.nasdaq_ConsumerStaples)
    tst.removeLastRecFromTable(markets_enum.nasdaq_ConsumerDiscretionary)

    #tst.sqlachemyTst()
    #tst.UpdateMarketData(markets_enum.ftse100)
    # tst.UpdateMarketData(markets_enum.ftse250)
    # tst.UpdateMarketData(markets_enum.dow)
    # tst.UpdateMarketData(markets_enum.s_and_p)
    # tst.UpdateMarketData(markets_enum.nasdaq)

    #tst.updateHistoryDataFTSE(ftse_enum.ftse100)
    #print(tst.get_stocks_list(ftse_enum.ftse250))
    # print(tst.mod_table_name("gg"))
    # print(date.today())

    #tst.repeat_clean()

    #tst.removeDotL()

    #tst.tableBuilder()
