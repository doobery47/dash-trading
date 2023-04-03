# read the values from the databases one ticker at time.
# analyse the data
# update the analysis table for each ticker

#https://www.youtube.com/watch?v=exGuyBnhN_8

import numpy as np
import pandas as pd
import pandas
from BaseHelper import BaseHelper
import pandas as pd
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import talib
from patterns import candlestick_patterns, candlestick_patterns_urls
from DataInterfaceHelper import dataInterfaceHelper
from dash import html
import logging


class CandlestickAnalHelper(BaseHelper):
    def __init__(self):
        BaseHelper.__init__(self)

    def is_consolidating(self, df, percentage):
        recent_candelsticks = df[-15:]        
        max_close= recent_candelsticks['close'].max()
        min_close= recent_candelsticks['close'].min()       
        threshold=1-(percentage/100)
        
        if min_close >(max_close * threshold):
            return True  
        
        return False  

    def is_breakingout(self, df, breakout_perc,breakout_trading_range):
        dd=df[-1:]['close']
        last_close=df[-1:]['close'].values[0]
        if(self.is_consolidating(df[:-1], breakout_perc)):
            range=-abs(breakout_trading_range)
            recent_close=df[range:-1]
            
            if(last_close >recent_close['close'].max()):
                return True
        
        return False

    def consolidating(self, marketsE,breakout_perc=10,breakout_trading_range=20):       
        breakout_list = []
        sql = """INSERT INTO ticket_errors(epic, name, reason, timestamp) VALUES(%s,%s,%s,%s);"""

        tickers=self.getTickersList(marketsE)
        print("Started processing")
        for tickerNames in tickers:
            pattern="CDLBREAKAWAY"
        
            try:
                
                dfTicker = pandas.read_sql_query('SELECT * FROM public.'+
                                                 tickerNames.sqlTickerTableStr.lower()+
                                                 ' ORDER BY date DESC;', 
                                                 con=BaseHelper.conn)
                #BaseHelper.conn.execute("SELECT * FROM {} ORDER BY Date DESC;".format(ticker))
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
                if(self.is_breakingout(dfTicker,breakout_perc,breakout_trading_range)):
                    breakout_list.append(tickerNames)
                    print("{} is consolidating".format(tickerNames.tickerStrpName))
            except Exception as e: ## report the problem and remove entr from tickerr table
                logging.getLogger().error(str(e))
                continue
        return self.buildTickerNameDict(breakout_list,marketsE)
    
    def breakout(self, ticker, breakout_trading_range):
       
        df = pd.read_sql_query("SELECT * FROM "+ticker.sqlTickerTable+" ORDER BY date DESC LIMIT "+str(breakout_trading_range), self.conn)

#        df = df.rename(columns = {'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Adj Close': 'adj close', 'Volume': 'volume'})
        for i in (df.columns):
            if(i=='date'):
                continue
            df[i] = df[i].astype(float)
        df.index = pd.to_datetime(df.date)
        start_date = None
        if start_date:
            df = df[df.index >= start_date]
       
        return df
    
    def bbands(self, price, window_size=10, num_of_std=5):
        rolling_mean = price.rolling(window=window_size).mean()
        rolling_std = price.rolling(window=window_size).std()
        upper_band = rolling_mean + (rolling_std*num_of_std)
        lower_band = rolling_mean - (rolling_std*num_of_std)
        return rolling_mean, upper_band, lower_band
    
    def movingaverage(self, interval, window_size=10):
        window = np.ones(int(window_size))/float(window_size)
        return np.convolve(interval, window, 'same')
    
    def buildHeadrText(self,ticker, company, the_date, is_bear):
        for_colour = "#eeeeee"
        date_str = the_date.strftime("%Y")
        if (is_bear):
            direction = "Bearish"
            back_colour = "#f44336"
        else:
            direction = "Bullish"
            back_colour = "#0d6abe"
        
        return html.Div([
            html.Br(),
            html.P(direction, style={'margin-bottom': 0,'text-align': 'center','background-color':back_colour}),
            html.P(ticker, style={'margin-bottom': 0,'text-align': 'center'}),
            html.P(company, style={'margin-bottom': 0,'text-align': 'center'}),
            html.P(date_str, style={'margin-bottom': 0,'text-align': 'center'}),
            html.Br(),
        ])

    
    def getGraphDescTxt(self, last, tickerNames,marketsE,years_ago):
        if (last > 0):
           return self.buildHeadrText(tickerNames.tickerStrpName,
                self.get_company_name(tickerNames,marketsE), years_ago, False)
        if (last < 0):
            return self.buildHeadrText(tickerNames.tickerStrpName,
                self.get_company_name(tickerNames,marketsE), years_ago, True)
        
   
    def buildFigureAndDescTxt(self, marketE, tickerNames,df,pattern_function, pattern):
        di = dataInterfaceHelper()
        try:
            result = pattern_function(
            df['open'], df['high'], df['low'], df['close'])
            df[pattern]=result
            pattern_days = df[df[pattern] != 0]
            if(pattern_days.empty):
                return None,None
            print(pattern_days)
            years_ago = datetime.date.today() - relativedelta(years=1)
        except Exception as e:
            print (str(e))
        try:
            if (len(pattern_days) > 0):
                df = di.get_historical_data(tickerNames, str(years_ago))
                INCREASING_COLOR = '#17BECF'
                DECREASING_COLOR = '#7F7F7F'

                data = [dict(
                    type='candlestick',
                    open=df.open,
                    high=df.high,
                    low=df.low,
                    close=df.close,
                    x=df.index,
                    yaxis='y2',
                    name='GS',
                    increasing=dict(line=dict(color=INCREASING_COLOR)),
                    decreasing=dict(line=dict(color=DECREASING_COLOR)),
                )]

                layout = dict()

                fig = dict(data=data, layout=layout)

                # Create the layout object

                fig['layout'] = dict()
                fig['layout']['plot_bgcolor'] = 'rgb(250, 250, 250)'
                fig['layout']['xaxis'] = dict(rangeselector=dict(visible=True))
                fig['layout']['yaxis'] = dict(
                    domain=[0, 0.2], showticklabels=False)
                fig['layout']['yaxis2'] = dict(domain=[0.2, 0.8])
                fig['layout']['legend'] = dict(
                    orientation='h', y=0.9, x=0.3, yanchor='bottom')
                fig['layout']['margin'] = dict(t=40, b=40, r=40, l=40)

                # Add range buttons
                rangeselector = dict(
                    visible=True,
                    x=0, y=0.9,
                    bgcolor='rgba(150, 200, 250, 0.4)',
                    font=dict(size=13),
                    buttons=list([
                        dict(count=1,
                            label='reset',
                            step='all'),
                        dict(count=1,
                            label='1yr',
                            step='year',
                            stepmode='backward'),
                        dict(count=3,
                            label='3 mo',
                            step='month',
                            stepmode='backward'),
                        dict(count=1,
                            label='1 mo',
                            step='month',
                            stepmode='backward'),
                        dict(step='all')
                    ]))

                fig['layout']['xaxis']['rangeselector'] = rangeselector
                mv_y = self.movingaverage(df.close)
                mv_x = list(df.index)

                # Clip the ends
                mv_x = mv_x[5:-5]
                mv_y = mv_y[5:-5]

                fig['data'].append(dict(x=mv_x, y=mv_y, type='scatter', mode='lines',
                                        line=dict(width=1),
                                        marker=dict(color='#E377C2'),
                                        yaxis='y2', name='Moving Average'))

                # Set volume bar chart colors
                colors = []

                for i in range(len(df.close)):
                    if i != 0:
                        if df.close[i] > df.close[i-1]:
                            colors.append(INCREASING_COLOR)
                        else:
                            colors.append(DECREASING_COLOR)
                    else:
                        colors.append(DECREASING_COLOR)

                # Add volume bar chart

                fig['data'].append(dict(x=df.index, y=df.volume,
                                        marker=dict(color=colors),
                                        type='bar', yaxis='y', name='volume'))

                bb_avg, bb_upper, bb_lower = self.bbands(df.close)

                fig['data'].append(dict(x=df.index, y=bb_upper, type='scatter', yaxis='y2',
                                        line=dict(width=1),
                                        marker=dict(color='#ccc'), hoverinfo='none',
                                        legendgroup='Bollinger Bands', name='Bollinger Bands'))

                fig['data'].append(dict(x=df.index, y=bb_lower, type='scatter', yaxis='y2',
                                        line=dict(width=1),
                                        marker=dict(color='#ccc'), hoverinfo='none',
                                        legendgroup='Bollinger Bands', showlegend=False))
                return self.getGraphDescTxt(pattern_days[pattern].iloc[-1], tickerNames,marketE,years_ago), fig
        except Exception as e:
                logging.getLogger().error(str(e))
                print(str(e))
