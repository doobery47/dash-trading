# read the values from the databases one ticker at time.
# analyse the data
# update the analysis table for each ticker

#https://www.youtube.com/watch?v=exGuyBnhN_8

import psycopg2
import pandas as pd
import pandas
from DataBaseHelper import DataBaseHelper
import mplfinance as mpf
import pandas as pd
from datetime import date


class CandlestickAnalHelper(DataBaseHelper):
    def __init__(self):
        DataBaseHelper.__init__(self)

    def is_consolidating(self, df, ticker, percentage):
        recent_candelsticks = df[-15:]        
        max_close= recent_candelsticks['close'].max()
        min_close= recent_candelsticks['close'].min()       
        threshold=1-(percentage/100)
        
        if min_close >(max_close * threshold):
            return True  
        
        return False  

    def is_breakingout(self, df, ticker, breakout_perc,breakout_trading_range):
        dd=df[-1:]['close']
        last_close=df[-1:]['close'].values[0]
        if(self.is_consolidating(df[:-1], ticker, breakout_perc)):
            range=-abs(breakout_trading_range)
            recent_close=df[range:-1]
            
            if(last_close >recent_close['close'].max()):
                return True
        
        return False

    def consolidating(self, marketsE,breakout_perc,breakout_trading_range):       
        breakout_list = []
        sql = """INSERT INTO ticket_errors(epic, name, reason, timestamp) VALUES(%s,%s,%s,%s);"""

        ftseTickers=self.get_stocks_list(marketsE)
        print("Started processing")
        for tickerNames in ftseTickers:
            pattern="CDLBREAKAWAY"
        
            try:
                
                dfTicker = pandas.read_sql_query('SELECT * FROM public."'+
                                                 tickerNames.sqlTickerTableStr.lower()+
                                                 '" ORDER BY date DESC;', 
                                                 con=DataBaseHelper.conn)
                #DataBaseHelper.conn.execute("SELECT * FROM {} ORDER BY Date DESC;".format(ticker))
                #row=cur.fetchall()
                # pattern_function = getattr(talib, pattern)
                # try:
                #     results = pattern_function(dfTicker['Open'], dfTicker['High'], dfTicker['Low'], dfTicker['Close'])
                #     print(results)
                #     last = results.tail(1).values[0]

                #     if last > 0:
                #         print(ticker+": bullish")
                #         #stocks[symbol][pattern] = 'bullish'
                #     elif last < 0:
                #         print(ticker+": bearish")
                #         #stocks[symbol][pattern] = 'bearish'
                #     else:
                #         print(ticker+": none")
                #         #stocks[symbol][pattern] = None
                # except: #psycopg2.OperationalError as e:
                #     print('failed on filename: ', ticker)
                #     continue
                if(self.is_breakingout(dfTicker, tickerNames.tickerStrpName,breakout_perc,breakout_trading_range)):
                    breakout_list.append(tickerNames.tickerStrpName)
                    print("{} is consolidating".format(tickerNames.tickerStrpName))
            except Exception as e: ## report the problem and remove entr from tickerr table
                DataBaseHelper.conn.execute(sql, (tickerNames.tickerStrpName,tickerNames.tickerStrpName,str(e),date.today().strftime('%Y-%m-%d'),))
                DataBaseHelper.session.commit()   
                continue
        return breakout_list
    
    def breakout(self, breakout, breakout_trading_range, chart_type, show_nontrading_days, chart_style):
       
        df = pd.read_sql_query("SELECT * FROM "+self.mod_table_digit_name(breakout)+" ORDER BY date DESC LIMIT "+str(breakout_trading_range), self.conn)

#        df = df.rename(columns = {'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Adj Close': 'adj close', 'Volume': 'volume'})
        for i in (df.columns):
            if(i=='date'):
                continue
            df[i] = df[i].astype(float)
        df.index = pd.to_datetime(df.date)
        start_date = None
        if start_date:
            df = df[df.index >= start_date]

        fig, ax = mpf.plot(
            df,
            title=f'{breakout}',
            type=chart_type,
            show_nontrading=show_nontrading_days,
            mav=(int(breakout_trading_range)),
            volume=True,
            style=chart_style,
            figratio=(30,12),
            
            # Need this setting for Streamlit, see source code (line 778) here:
            # https://github.com/matplotlib/mplfinance/blob/master/src/mplfinance/plotting.py
            returnfig=True
        )
        
        return fig, df
        