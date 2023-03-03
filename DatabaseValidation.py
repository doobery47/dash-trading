from marketsenum import markets_enum
from sectorenum import sector_enum
import pandas as pd
import pandas_datareader as pdr
from BaseHelper import BaseHelper
from datetime import date, datetime,timedelta
import yfinance as yf
from industries import ind,sector
import logging
from dateutil import parser
import public_holiday
from pandas.tseries.holiday import USFederalHolidayCalendar
import holidays


import sys


class DatabaseValidation(BaseHelper):
    
    def __init__(self):
        BaseHelper.__init__(self)
        
    def checkDates(self, marketE):
        weekdaysLst=[]
        tickers = self.get_stocks_list(marketE)
        for ticker in tickers:
            df = pd.read_sql_query("SELECT date from "+ticker.sqlTickerTableStr, BaseHelper.conn)
            start=df.loc[df.index[0], 'date']
            # get the first and last dates
            a=df.head(1)
            b=df.tail(1)
            weekno = datetime.today().weekday()
            last=b.loc[b.index[0], 'date']
            ll=pd.date_range(start = start.isoformat(), end = last.isoformat() ).difference(df.date)
            lst= ll.to_native_types().tolist()

            for d in lst:
                yourdate = parser.parse(d)
                weekno = yourdate.weekday()

                if weekno < 5:
                    cal = USFederalHolidayCalendar()
                    #holidays = cal.holidays(start=start.isoformat(), end=last.isoformat()).to_pydatetime()
                    us_holidays = holidays.US()

                    if yourdate in us_holidays:
                        continue
                    else:
                        weekdaysLst.append({ticker.sqlTickerTableStr,d})
                else:
                    continue
                # else:  # 5 Sat, 6 Sun
                #     print ("Weekend")
        print(weekdaysLst)
            
            
    def Logger(self, file_name):
        formatter = logging.Formatter(
            fmt="%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s",
            datefmt="%Y/%m/%d %H:%M:%S",
        )  # %I:%M:%S %p AM|PM format
        logging.basicConfig(
            filename="%s.log" % (file_name),
            format="%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s",
            datefmt="%Y/%m/%d %H:%M:%S",
            filemode="a",
            level=logging.DEBUG,
        )
        LOG = logging.getLogger()
        LOG.setLevel(logging.DEBUG)

        # console printer
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logging.getLogger().addHandler(screen_handler)

        LOG.info("Logger object created successfully..")
        return LOG
            
if __name__ == "__main__":
    dv = DatabaseValidation()
    LOG = dv.Logger("DatabaseValidation")
    dv.checkDates(markets_enum.dow)