from yahoofinancials import YahooFinancials
from yahoo_fin import stock_info as si
import yfinance as yf

import pandas as pd
from DataInterfaceHelper import dataInterfaceHelper
from datetime import date, datetime, timedelta



# This is a layer to retrieve data from external interfaces ie yahoo and then convert
# the data into an internal consumable format.

from yahoofinancials import YahooFinancials

class ExtFinanceInterface():
    def __init__(self):
        print("ExtFinanceInterface _init__")
        
    ## tickerDay has to be last day that is being analysed. We use this ti get the previous close value
    def getTickerData(self, ticker, marketE):
        yahooPattern="https://uk.finance.yahoo.com/quote/{}?p={}&.tsrc=fin-srch".format(ticker.tickerYahoo.upper(),ticker.tickerYahoo.upper())
        dih = dataInterfaceHelper()
        
        pd.set_option("display.max_colwidth", -1)

        sectorName=dih.get_sector_name(ticker, marketE)
        sector=sectorName
        yahoo  = yahooPattern


        data = [
            ["sector", sector],
            ['yahoo', yahooPattern]
          
        ]
        
        retList={"sector": sector,
            "yahoo": yahooPattern}

        # Create the pandas DataFrame
        df = pd.DataFrame(data, columns=["Name", "Description"])
        # df = df.to_html(escape=False)
        return df,retList
        
        
    def getTickerDataTest(self, ttv, marketE):
        # pandas display options
        pd.set_option("display.max_colwidth", -1)

        sector = "financial"
        longBusinessSummary = "s simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book."
        grossProfits = 2938000000
        previousClose=23.44
        currentPrice=22.22
        increase=0.23
        profitMargins = 0.13743
        priceToBook=7.7
        totalCash = 970000000
        totalDebt = 4012999936
        forwardEps = 0.18
        bookValue = 0.909
        forwardPE = 7.5444446
        longName = ttv.ticker + " bla bla bla"
        companyURL = "https://www.bbc.co.uk/news"
        website = f'<a target="_blank" href="{companyURL}">Company URL</a>'
        if grossProfits > 1000000:
            grossProfits = str(round(grossProfits / 1000000, 2)) + "m"
            totalCash = str(round(totalCash / 1000000, 2)) + "m"
            totalDebt = str(round(totalDebt / 1000000, 2)) + "m"
        
        data = [
            ["sector", sector],
            ["current price", currentPrice],
            ["previous close", previousClose],
            ["increase", str(increase) + "%"],
            ["gross profits", grossProfits],
            ["profit margins", profitMargins],
            ["total cash", totalCash],
            ["total debt", totalDebt],
            ["forward EPS", forwardEps],
            ["book value", bookValue],
            ["price to book", priceToBook],
            ["forward PE", forwardPE],
            ["website", website],
        ]
        
        retList={"sector": sector,
            "current price": currentPrice,
            "previous close": previousClose,
            "increase": str(increase) + "%",
            "gross profits": grossProfits,
            "profit margins": profitMargins,
            "total cash": totalCash,
            "total debt": totalDebt,
            "forward EPS": forwardEps,
            "book value": bookValue,
            "price to book": priceToBook,
            "forward PE": forwardPE,
            "website": website}

        # Create the pandas DataFrame
        df = pd.DataFrame(data, columns=["Name", "Description"])
        #df = df.to_html(escape=False)
        return df,retList

    # def getTickerData(self, ticker, marketE):
    #     pd.set_option("display.max_colwidth", -1)
    #     stock = yf.Ticker(ticker.tickerYahoo)
    #     addInfo=stock.fast_info
    #     dict = stock.info
    #     sector = dict["sector"]
    #     grossProfits = dict["grossProfits"] 
    #     profitMargins = dict["profitMargins"]
    #     totalCash = dict["totalCash"]
    #     totalDebt = dict["totalDebt"]
    #     forwardEps = dict["forwardEps"]
    #     bookValue = dict["bookValue"]
    #     forwardPE = dict["forwardPE"]
    #     website = dict["website"]
    #     currentPrice = round(addInfo["last_price"],2)
    #     previousClose = round(addInfo["previous_close"],2)
    #     priceToBook = dict["priceToBook"]
    #     # website = f'<a target="_blank" href="{website}">Company URL</a>'
    #     increase = round(
    #         100 * (float(currentPrice) - float(previousClose)) / float(previousClose), 3
    #     )

    #     try:
    #         if grossProfits is not None and grossProfits > 1000000:
    #             grossProfits = str(round(grossProfits / 1000000, 2)) + "m"
    #         if totalCash is not None and totalCash > 1000000:
    #             totalCash = str(round(totalCash / 1000000, 2)) + "m"
    #         if totalDebt is not None and totalDebt >1000000:
    #             totalDebt = str(round(totalDebt / 1000000, 2)) + "m"
    #     except Exception as e:
    #         print (e)

    #     data = [
    #         ["sector", sector],
    #         ["current price", currentPrice],
    #         ["previous close", previousClose],
    #         ["increase", str(increase) + "%"],
    #         ["gross profits", grossProfits],
    #         ["profit margins", profitMargins],
    #         ["total cash", totalCash],
    #         ["total debt", totalDebt],
    #         ["forward EPS", forwardEps],
    #         ["book value", bookValue],
    #         ["price to book", priceToBook],
    #         ["forward PE", forwardPE],
    #         ["website", website],
    #     ]
        
    #     retList={"sector": sector,
    #         "current price": currentPrice,
    #         "previous close": previousClose,
    #         "increase": str(increase) + "%",
    #         "gross profits": grossProfits,
    #         "profit margins": profitMargins,
    #         "total cash": totalCash,
    #         "total debt": totalDebt,
    #         "forward EPS": forwardEps,
    #         "book value": bookValue,
    #         "price to book": priceToBook,
    #         "forward PE": forwardPE,
    #         "website": website}

    #     # Create the pandas DataFrame
    #     df = pd.DataFrame(data, columns=["Name", "Description"])
    #     # df = df.to_html(escape=False)
    #     return df,retList
 
    
 
if __name__ == "__main__":
    from BaseHelper import TickerTypeVals, BaseHelper
    from marketsenum import markets_enum
    efi = ExtFinanceInterface()
    dbh=BaseHelper()
    marketE=markets_enum['ftse100']
    ticker= dbh.getTicker("BP.",marketE)
    dat = datetime(2023, 2, 20,)
    data=efi.getTickerData(ticker, marketE, dat)
    print(data)
        
    