from marketsenum import markets_enum
from sectorenum import sector_enum
import pandas as pd
import pandas_datareader as pdr
from BaseHelper import BaseHelper
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
import yfinance as yf
from yahoo_fin import stock_info as si
from industries import ind, sector
import pandas
import logging
import sqlalchemy
import numpy as np
import feedparser
from dash import Dash, html, dcc, Output, Input, callback, State, MATCH
import tradingExcpetions as tex


class dataInterfaceHelper(BaseHelper):
    FTSE100 = "https://www.marketwatch.com/investing/index/ukx/downloaddatapartial?startdate={}&enddate={}&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false&countrycode=uk"
    FTSE250 = "https://www.marketwatch.com/investing/index/mcx/downloaddatapartial?startdate={}&enddate={}&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false&countrycode=uk"
    DowJones = "https://www.marketwatch.com/investing/index/djia/downloaddatapartial?startdate={}&enddate={}&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false"
    NASDAQ = "https://www.marketwatch.com/investing/index/comp/downloaddatapartial?startdate={}&enddate={}&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false"
    S_AND_P = "https://www.marketwatch.com/investing/index/spx/downloaddatapartial?startdate={}&enddate={}&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false"

    marketDict = {
        markets_enum.ftse100.name: FTSE100,
        markets_enum.ftse250.name: FTSE250,
        markets_enum.dow.name: DowJones,
        markets_enum.nasdaq.name: NASDAQ,
        markets_enum.s_and_p.name: S_AND_P,
    }

    def __init__(self):
        BaseHelper.__init__(self)

    def get_marketData(self, marketE, period=1, sec=sector_enum.none):
            
        tableName = marketE.name + "_historic_values"
        startDate=self.holidayDateAdjust(datetime.now() - relativedelta(years=period), marketE)
        #startDate = (datetime.now() + timedelta(days=((period*365)-1)*-1)).date()
        if sec != sector_enum.none and marketE == markets_enum.nasdaq:
            df = pd.read_sql_query(
                "SELECT * from {} WHERE sector='{}' and \"date\" >= '{}' ORDER BY date DESC;".format(
                    tableName, self.getSectorStringVal(sec), str(startDate)
                ),
                BaseHelper.conn,
            )
        else:
            df = pd.read_sql_query(
                "SELECT * from {} WHERE \"date\" >= '{}' ORDER BY date DESC;".format(
                    tableName, str(startDate)
                ),
                BaseHelper.conn,
            )
            
        df.drop_duplicates(subset="date", keep='first', inplace=True)
        for i in df.columns:
            if i == "date":
                continue
            df[i] = df[i].astype(float)

        df.index = pd.to_datetime(df.date)
        df = df.sort_index()        
        return df

    def get_ticker_data(self, ticker):
        # ticker=self.mod_table_digit_name(ticker)
        # ticker="\""+ticker+"\""
        df = pd.read_sql_query(
            "SELECT * FROM public." + ticker.sqlTickerTableStr, BaseHelper.conn
        )
        return df
    
    

        
    def get_historical_data(self, ticker, start_date=None, live=False):
        df = None
        if live:
            try:
                if(start_date==None):
                    start_date = datetime.strptime("2017-07-30", "%Y-%m-%d").date()
                tickerData = yf.Ticker(ticker.tickerYahoo)
                delta = datetime.now().date() - start_date
                df = tickerData.history(period=str(delta.days) + "d")
                df = df.drop("Dividends", axis=1)
                df = df.drop("Stock Splits", axis=1)
                # df = pdr.get_data_yahoo(ticker.tickerYahoo, start=start_date, end=datetime.now())
                df.rename(
                    columns={
                        "Open": "open",
                        "Close": "close",
                        "High": "high",
                        "Low": "low",
                        "Volume": "volume",
                        "Date": "date",
                    },
                    inplace=True,
                )
                for i in df.columns:
                    if i == "date":
                            continue
                    df[i] = df[i].astype(float)
                df.index = pd.to_datetime(df.date)
                # start_date = None
                if start_date:
                    df = df[df.index >= start_date]
                return self.__validateHistory(df, ticker)
            except Exception as e:
                print(ticker.sqlTickerTableStr + " :" + str(e))
                logging.getLogger().error(ticker.sqlTickerTableStr + " :" + str(e))
        else:
            try:
                df = pd.read_sql_query("SELECT * FROM " + ticker.sqlTickerTableStr, BaseHelper.conn)
                df.drop_duplicates(subset="date", keep='first', inplace=True)
                for i in df.columns:
                    if i == "date":
                        continue
                    df[i] = df[i].astype(float)
                df.index = pd.to_datetime(df.date)
                if start_date:
                    df = df[df.index >= start_date]
                    
                return df.sort_index() 
            except Exception as e:
                print(ticker.sqlTickerTableStr + " :" + str(e))
                logging.getLogger().error(ticker.sqlTickerTableStr + " :" + str(e))

        # try:
        #     df.index = pd.to_datetime(df.index).date
        #     print(df.index)

        #     if start_date:
        #         df = df[df.index >= start_date]
        #     df.to_csv("get_historical_data.csv")
        #     return df
        # except Exception as e:
        #     print(ticker.sqlTickerTableStr + " :" + str(e))

    def UpdateMarketData(self, marketE, sec=sector_enum.none):
        df = self.get_marketData(marketE, 1,sec)
        df["date"] = pd.to_datetime(df["date"])
        if df.size == 0:  # We have an empty table
            startDate = datetime.now() + timedelta(days=-364)
        elif df.size > 0:
            df2 = df.iloc[-1]
            lastDate = df2["date"]
            startDate = (pd.to_datetime(lastDate) + pd.DateOffset(days=1)).date()
            if startDate >= date.today():  # - timedelta(days=1)):
                print(
                    "Wont process "
                    + marketE.name
                    + " as end date is equal to or greater than today"
                )
                return

        startDateStr = startDate.strftime("%m/%d/%Y")
        endDateStr = datetime.now().strftime("%m/%d/%Y")
        marketStr = self.marketDict[marketE.name]
        market = marketStr.format(startDateStr, endDateStr)

        df = pd.read_csv(market)
        df.rename(
            columns={
                "Open": "open",
                "Close": "close",
                "High": "high",
                "Low": "low",
                "Volume": "volume",
                "Date": "date",
            },
            inplace=True,
        )
        df["close"] = df["close"].str.replace("\,", "", regex=True)
        df["open"] = df["open"].str.replace("\,", "", regex=True)
        df["high"] = df["high"].str.replace("\,", "", regex=True)
        df["low"] = df["low"].str.replace("\,", "", regex=True)
        df["date"] = pd.to_datetime(df["date"])
        df.to_sql(
            marketE.name + "_historic_values",
            con=BaseHelper.engine,
            if_exists="append",
            index=False,
        )
        BaseHelper.session.commit()

    def updateHistoryDataForTicker(self, tickerNameContainer,marketValE):
        # get last record and date form table

        startDate = datetime.strptime("2017-07-30", "%Y-%m-%d").date()
        try:
            if self.tableExists(tickerNameContainer.sqlTickerTableStr):
                df_db = pd.read_sql_query(
                    "SELECT * FROM {} ORDER BY date DESC LIMIT 1;".format(
                        tickerNameContainer.sqlTickerTableStr
                    ),
                    BaseHelper.conn,
                )
                startDate = (
                    pd.to_datetime(df_db["date"][0]) + pd.DateOffset(days=1)
                ).date()
                if startDate >= date.today():
                    status = (
                        "Wont process "
                        + tickerNameContainer.tickerStrpName
                        + " as end date is equal to or greater than today"
                    )
                    return status
            else:  # no table found so we will create one and set up some default data
                self.createTable(tickerNameContainer.sqlTickerTableStr)
        except Exception as e:  ## report the problem and remove entr from tickerr table
            #delStr="DELETE FROM "+marketValE+" WHERE epic='"+tickerNameContainer.sqlTickerTableStr+"'"
            logging.getLogger().error("DELETE FROM "+marketValE.name+" WHERE epic='"+tickerNameContainer.sqlTickerTableStr.upper()+"';")
            #logging.getLogger().error(str(e))
            raise e

        try:
            df = yf.download(
                tickerNameContainer.tickerYahoo,
                start=startDate,
                end=date.today(),
                group_by="ticker",
            )
            print(df)
            if "Dividends" in df.columns:
                df = df.drop("Dividends", axis=1)
            if "Stock Splits" in df.columns:
                df = df.drop("Stock Splits", axis=1)
            df.to_csv("test.csv")
            data = pd.read_csv("test.csv")
            print("processed: " + tickerNameContainer.tickerStrpName)
        except Exception as e:
            logging.getLogger().error(str(e))
            logging.getLogger().error("DELETE FROM "+marketValE.name+" WHERE epic='"+tickerNameContainer.sqlTickerTableStr.upper()+"';")
 
            raise e

        data.rename(
            columns={
                "Open": "open",
                "Close": "close",
                "High": "high",
                "Low": "low",
                "Volume": "volume",
                "Date": "date",
            },
            inplace=True,
        )
        data.date = pd.to_datetime(data.date)
        print(data)
        # need to set table name to lower as panda puts name in double quotes as we need a lower case name
        data.to_sql(
            tickerNameContainer.sqlTickerTable,
            con=BaseHelper.conn,
            schema="public",
            if_exists="append",
            index=False,
        )
        BaseHelper.session.commit()
        return "Complete"
                 
    def getRssNews(self, ticker, fontSize='14px'):
        if isinstance(ticker, str):
            feed=feedparser.parse("https://feeds.finance.yahoo.com/rss/2.0/headline?s="+ticker+"&region=US&lang=en-US")
        else:
            feed=feedparser.parse("https://feeds.finance.yahoo.com/rss/2.0/headline?s="+ticker.tickerYahoo+"&region=US&lang=en-US")
        children=[]
        for entry in feed.entries:
            lnk=html.Div([html.A(entry.summary, href=entry.link, target="_blank",style={"marginBottom": "5px",'fontSize': fontSize,})],)
            children.append(lnk)        
        return children
    
    def getPreviousDayClose(self, ticker, marketE, lastKnownDate):
        lastKnownDate=self.holidayDateAdjust(lastKnownDate, marketE)
        datStr="'"+str(lastKnownDate)+"'"
        df = pd.read_sql_query('SELECT close FROM ' + ticker.sqlTickerTable+' where "date"='+datStr+';', BaseHelper.conn)
        if(df.empty):
            raise tex.StockOutofDateException
        else:
            prevClose=df['close'][0]
        return prevClose
                           
    def getMarketTicker(self, marketE):
        if marketE == markets_enum.ftse100:
            marketStr = "^FTSE"
        elif marketE == markets_enum.ftse250:
            marketStr = "^FTMC"
        elif marketE == markets_enum.dow:
            marketStr = "^DJI"
        elif marketE == markets_enum.nasdaq:
            marketStr = "NQ=F"
        elif marketE == markets_enum.s_and_p:
            marketStr = "^GSPC"
            
        return marketStr

    def getMarketCurrentValue(self, marketE):
        marketStr = self.getMarketTicker(marketE)
        
        #ticker = yf.Ticker(marketStr).info
        return si.get_live_price(marketStr)
        #return ticker["regularMarketPrice"], ticker["previousClose"]

    def tableBuilder(self):
        # select each industry in turn.
        # create a table
        # get the values from the nasdaq table
        # add these rows into the created table

        f = open("nasdaqSort.txt", "w")
        for i in sector:
            ticks = pandas.read_sql_query(
                "SELECT epic,name,ipo_year,sector,country,industry,last_update from nasdaq WHERE sector='"
                + i
                + "'",
                con=BaseHelper.conn,
            )
            ticks.to_sql(
                "nasdaq_" + i, con=BaseHelper.conn, if_exists="append", index=False
            )
            BaseHelper.session.commit()
            # for tick in ticks.iterrows():
            #     print(tick)
            # f.write(ticks.to_string()+" : "+count(ticks)+i+"\n")
            print(ticks)
        f.close()

    def removeLastRecFromTable(self, marketE):
        tickers = self.getTickersList(marketE)
        for ticker in tickers:
            lTicker = ticker.sqlTickerTableStr.lower()
            try:
                BaseHelper.conn.execute(
                    'DELETE FROM "'
                    + lTicker
                    + '" WHERE date in(SELECT MAX("date") FROM "'
                    + lTicker
                    + '") '
                )
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

    tst = dataInterfaceHelper()
    # tst.removeLastRecFromTable(markets_enum.ftse100)
    # tst.removeLastRecFromTable(markets_enum.dow)
    # tst.removeLastRecFromTable(markets_enum.nasdaq_BasicMaterials)
    # tst.removeLastRecFromTable(markets_enum.nasdaq_ConsumerStaples)
    # tst.removeLastRecFromTable(markets_enum.nasdaq_ConsumerDiscretionary)
    #tst.removequotedTables(markets_enum.ftse100)
    # tst.deleteDuplicateRows(markets_enum.ftse250)

    # tst.sqlachemyTst()
    # tst.UpdateMarketData(markets_enum.ftse100)
    # tst.UpdateMarketData(markets_enum.ftse250)
    # tst.UpdateMarketData(markets_enum.dow)
    # tst.UpdateMarketData(markets_enum.s_and_p)
    # tst.UpdateMarketData(markets_enum.nasdaq)

    # tst.updateHistoryDataFTSE(ftse_enum.ftse100)
    # print(tst.get_stocks_list(ftse_enum.ftse250))
    # print(tst.mod_table_name("gg"))
    # print(date.today())
    marketE=markets_enum['ftse100']
    ticker= tst.getTicker("BP.",marketE)
    dat = datetime(2021, 2, 20,)
    dat=dat-timedelta(days=1)
    #xx=tst.getPreviousDayClose(ticker,marketE,dat)
    
    for ticker in tst.getTickersList(marketE):  
        if(ticker.ticker=='CPG'):
            print('here')
        df=tst.get_historical_data(ticker,str(dat))
        print(df)
    


    # tst.repeat_clean()

    # tst.removeDotL()

    # tst.tableBuilder()
