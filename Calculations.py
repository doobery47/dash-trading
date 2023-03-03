# This will be clas that is used to perform various stock calculations (only)
#%%

from BaseHelper import BaseHelper
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
from DataInterfaceHelper import dataInterfaceHelper
from marketsenum import markets_enum
import matplotlib.pyplot as plt
from DataInterfaceHelper import dataInterfaceHelper


class TradingCalculations(BaseHelper):
    def __init__(self):
        BaseHelper.__init__(self)
        
    dih = dataInterfaceHelper()
        
     ###
    # Linear regression 
    # https://blog.quantinsti.com/linear-regression-market-data-python-r/
    ##
    def log_returns(self, data):
        return np.log(data/data.shift())
    
    def epocTime(self,dtSeries):
        dVals = []
        
        for dt in dtSeries:       
            epoch = int((dt - datetime(1970,1,1).date()).total_seconds())/10000
            dtSeries = dtSeries.replace(to_replace = dt, value = epoch)

        return dtSeries
        
     
    # build a linear regression graph where we take a ticker as Y and the market (ie ftse100) as X
    def linear_regression(self, ticker, marketE):
        today = self.holidayDateAdjust(datetime.now() - timedelta(days=1), marketE)
        one_yrs_ago = self.holidayDateAdjust(datetime.now() - relativedelta(years=1), marketE)
        two_yrs_ago = self.holidayDateAdjust(datetime.now() - relativedelta(years=2), marketE)
        #three_yrs_ago = self.dateMove(datetime.now() - relativedelta(years=3), marketE)
        tickerHistory=self.dih.get_historical_data(ticker,str(two_yrs_ago))
        marketHistory=self.dih.get_marketData(marketE, 2)

        # clean the data
        marketHistory=marketHistory.loc[marketHistory['date'].isin(tickerHistory['date'])]
        tickerHistory=tickerHistory.loc[tickerHistory['date'].isin(marketHistory['date'])]
        #tickerHistory.drop_duplicates(subset="date", keep='first', inplace=True)
        #marketHistory.drop_duplicates(subset="date", keep='first', inplace=True)
         


        # mh=marketHistory['date']
        # th=tickerHistory['date']
        # print(len(mh))
        # print(len(th))
        # print(len(mh.unique()))
        # print(len(th.unique()))
        # for x in th:
        #     if(x in mh.values):
        #         print("found "+str(x) +" in mh")
        #     else:
        #         print("Not found "+str(x) +" in mh")
                
        # print([item for item, count in collections.Counter(th).items() if count > 1])

                
        # mh_df = mh.to_frame()
        # th_df=th.to_frame()
        # mh_df.reset_index(drop = True, inplace = True)
        # th_df.reset_index(drop = True, inplace = True)
        
        # merged = mh_df.merge(th_df, indicator=True, how='outer')
        # merged[merged['_merge'] == 'right_only']
        # merged.to_csv("merged.csv")
        
        # marketHistory.to_csv('marketHistory.csv')
        # tickerHistory.to_csv('tickerHistory.csv')
        
        
        tickerClose=tickerHistory['close']
        marketClose=marketHistory['close']
        
        ticker_log_returns = np.log(tickerClose/tickerClose.shift())
        market_log_returns = np.log(marketClose/marketClose.shift())
        #print(market_log_returns)
        
        X = ticker_log_returns.iloc[1:].to_numpy().reshape(-1, 1)
        Y = market_log_returns.iloc[1:].to_numpy().reshape(-1, 1)
        
        lin_regr = LinearRegression()
        lin_regr.fit(X, Y)

        Y_pred = lin_regr.predict(X)
        
        X2=np.reshape(X, -1)
        Y2=np.reshape(Y, -1)
        Y_pred2=np.reshape(Y_pred, -1)

        alpha = lin_regr.intercept_[0]
        beta = lin_regr.coef_[0, 0]
        #return X2,Y2,Y_pred2
        
        fig, ax = plt.subplots()
        tickerName=self.get_company_name(ticker, marketE)
        ax.set_title(tickerName+"-"+ticker.tickerStrpName)
        #ax.set_title("Alpha: " + str(round(alpha, 5)) + ", Beta: " + str(round(beta, 3)))
        ax.scatter(X, Y)
        ax.plot(X, Y_pred, c='r')
        
    cntFound=0
        
    def simpleLinearRegresion(self, df, ticker, marketE):
        today = self.holidayDateAdjust(datetime.now() - timedelta(days=1), marketE)
        one_yrs_ago = self.holidayDateAdjust(datetime.now() - relativedelta(years=1), marketE)
        two_yrs_ago = self.holidayDateAdjust(datetime.now() - relativedelta(years=2), marketE)
        #three_yrs_ago = self.dateMove(datetime.now() - relativedelta(years=3), marketE)
        dih = dataInterfaceHelper()
        
        
        # clean the data
        #tickerHistory.drop_duplicates(subset="date", keep='first', inplace=True)
        
        tickerDates=df['date']
        tickerVals=df['close']       
        tickerDates_int=self.epocTime(tickerDates)
        tickerVals.dropna()
        tickerDates_int.dropna()
        
        X = tickerDates_int.iloc[1:].to_numpy().reshape(-1, 1)
        Y = tickerVals.iloc[1:].to_numpy().reshape(-1, 1)
        try:
            lin_regr = LinearRegression()
            lin_regr.fit(X, Y)
        except Exception as e:
            print(e)

        Y_pred = lin_regr.predict(X)
        Y_pred2=np.reshape(Y_pred, -1)

        intercept = lin_regr.intercept_[0]
        slope = lin_regr.coef_[0, 0]
        
        # fig, ax = plt.subplots()
        # tickerName=self.get_company_name(ticker, marketE)
        # ax.set_title(tickerName+"-"+ticker.tickerStrpName)
        # #ax.set_title("Alpha: " + str(round(alpha, 5)) + ", Beta: " + str(round(beta, 3)))
        # ax.plot(X, Y)
        # ax.plot(X, Y_pred, c='r')
        return Y_pred2
        
    def find_second_point(self, slope,x0,y0):
        # this function returns a point which belongs to the line that has the slope 
        # inserted by the user and that intercepts the point (x0,y0) inserted by the user
        q = y0 - (slope*x0)  # calculate q
        new_x = x0 + 10  # generate random x adding 10 to the intersect x coordinate
        new_y = (slope*new_x) + q  # calculate new y corresponding to random new_x created

        return new_x, new_y  # return x and y of new point that belongs to the line
    
    
if __name__ == "__main__":
    di = TradingCalculations()
    #dd = di.topShares(markets_enum.ftse250)
    #print(dd)
    marketE=markets_enum.nasdaq_finance
    dih = dataInterfaceHelper()
    two_yrs_ago = dih.holidayDateAdjust(datetime.now() - relativedelta(years=2), marketE)
    for ticker in di.get_stocks_list(marketE):  
        df=dih.get_historical_data(ticker,str(two_yrs_ago))  
        di.simpleLinearRegresion(df,ticker,marketE)

        
# %%
