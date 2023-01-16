from marketsenum import markets_enum
from sectorenum import sector_enum
import pandas as pd
import re
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import Session
import config
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Float, BigInteger
import logging


class TickerTypeVals():
    def __init__(self, ticker, sqlMarketTableStr, sqlTickerTableStr, sqlTickerTable, tickerStrpName,
                 tickerYahoo):
        self.ticker = ticker
        self.sqlMarketTableStr = sqlMarketTableStr
        self.sqlTickerTableStr = sqlTickerTableStr
        self.tickerStrpName = tickerStrpName
        self.sqlTickerTable=sqlTickerTable
        self.tickerYahoo = tickerYahoo

    # This is vanilla value of the ticker. ie just name no market extension
    ticker = ""
    sqlTickerTableStr = ""  # To access ticker sql tables
    sqlMarketTableStr = ""  # Access the records in the market tables ie ft100
    tickerStrpName = ""     # As ticker but also "." removed, but add ZZ
    # if the company starts with a digit
    tickerYahoo = ""        # This contains the market extension ie ".L". None for US
    sqlTickerTable=""


class DataBaseHelper:
    conn = None
    engine = None
    session = None

    def __init__(self):
        user = config.DB_USER
        pwd = config.DB_PASS
        db = config.DB_NAME
        if (DataBaseHelper.engine == None):
            DataBaseHelper.engine = create_engine(
                'postgresql+psycopg2://'+user+':'+pwd+'@localhost:5432/'+db)
            DataBaseHelper.conn = DataBaseHelper.engine.connect()
            DataBaseHelper.session = Session(
                DataBaseHelper.engine, future=True)

    def getMarketEnum(self, mn):
        if (mn == "FTSE 100"):
            return markets_enum.ftse100
        elif (mn == "FTSE 250"):
            return markets_enum.ftse250
        elif (mn == "DOW"):
            return markets_enum.dow
        elif (mn == "NASDAQ"):
            return markets_enum.nasdaq
        elif (mn == "S&P"):
            return markets_enum.s_and_p
        else:
            return markets_enum.none

    def getSectorStringVal(self, se):
        if (se == sector_enum.BasicMaterials):
            return "Basic Materials"
        elif (se == sector_enum.ConsumerDiscretionary):
            return "Consumer Discretionary"
        elif (se == sector_enum.ConsumerStaples):
            return "Consumer Staples"
        elif (se == sector_enum.Energy):
            return "Energy"
        elif (se == sector_enum.Finance):
            return "Finance"
        elif (se == sector_enum.HealthCare):
            return "Health Care"
        elif (se == sector_enum.Industrials):
            return "Industrials"
        elif (se == sector_enum.Miscellaneous):
            return "Miscellaneous"
        elif (se == sector_enum.RealEstate):
            return "Real Estate"
        elif (se == sector_enum.Technology):
            return "Technology"
        elif (se == sector_enum.Telecommunications):
            "Telecommunications"
        elif (se == sector_enum.Utilities):
            return "Utilities"

    def get_company_name(self, tickerNames, marketsE):

        df = pd.read_sql_query("SELECT * FROM public.{} WHERE epic={};".format(marketsE.name,
                                                                                 tickerNames.sqlMarketTableStr), DataBaseHelper.conn)
        print(df)
        try:
            f = df['name']
            dd = df.iloc[0]['name']
            return dd
        except Exception as e:
            logging.getLogger().error(str(e))

    def get_stock_list_names(self, stockE):
        list = self.get_stocks_list(stockE)
        names = []
        for namesG in list:
            names.append(namesG.tickerStrpName)
        return names

    def tableExists(self, tableName):
        tableName=tableName.replace('"','') #NOTE. Need to remove the quites to run the next statement
        return sqlalchemy.inspect(self.engine).has_table(tableName)

    def createTable(self, tableName):
        tableName=tableName.replace('"','')  #NOTE. Need to remove the quites to run the next statement
        meta = MetaData() 
        tab = Table(
            tableName, meta,
            Column('date', Date),
            Column('open', Float),
            Column('high', Float),
            Column('low', Float),
            Column('close', Float),
            Column('Adj Close', Float),
            Column('volume', BigInteger),
        )
        meta.create_all(self.engine)

    def get_compound_ticker_name(self, ticker, stockE):
        if(ticker.lower()=="av."):
            print("here")
        tickerYahooExt = ""  # default value
        if (stockE == markets_enum.ftse100):
            tickerYahooExt = ".L"
        elif (stockE == markets_enum.ftse250):
            tickerYahooExt = ".L"
        tickerStrpName = re.sub("[.]", "", ticker)
        sqlTickerTableStr = '"'+self.getTickerSQLName(ticker)+'"' # with quotes
        sqlTickerTable = self.getTickerSQLName(ticker) # without quotes
        sqlMarketTableStr = "'"+ticker.upper()+"'" # This is used to get the ticker value out of the market tables. They are all uppercase
        tickerYahoo = tickerStrpName+tickerYahooExt
        #tickerYahoo=re.sub("[..]", ".", tickerYahoo)

        ttv = TickerTypeVals(ticker, sqlMarketTableStr,
                             sqlTickerTableStr, sqlTickerTable, ticker, tickerYahoo)
        return ttv

    # the return list consist of tuples containing a the sqlformat name, the true name
    def get_stocks_list(self, stockE):
        df = self.query_columns_to_dataframe(stockE.name, ['epic'])
        tickers = df['epic']
        print("Started processing")

        new_ticker_lst = []

        print(tickers)
        for ticker in tickers:
            new_ticker_lst.append(self.get_compound_ticker_name(ticker, stockE))

        return new_ticker_lst
    
    def buildTickerNameDict(self, tickers, marketE):
        #{'label': 'FTSE 100', 'value': 'ftse100'}
        tickerNames=[]
        for ticker in tickers:
            busName=self.get_company_name(ticker,marketE)
            tickerNames.append({'label': busName, 'value': ticker.tickerStrpName})
        return tickerNames
            
            

    def query_columns_to_dataframe(self, table, columns):
        query = 'select '
        for i in range(len(columns)):
            query = query + columns[i] + ', '
        query = query[:-2] + ' from "' + table+'"'
        df = pd.read_sql_query(query, DataBaseHelper.conn)
        return df

    # def mod_table_digit_name(self, ticker):
    #     if (ticker[0].isdigit()):
    #         return "zz_"+ticker
        
    #     else:
    #         return ticker.lower()

    def getTickerSQLName(self, ticker):
        if (ticker[0].isdigit()):
            return "zz_"+ticker.lower()
        elif(ticker.endswith('.')):
            return ticker.replace(".", "_yy").lower()
        else:
            return ticker.lower()
        
