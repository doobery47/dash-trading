


import pandas as pd
from BaseHelper import BaseHelper
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas
from dash import dash_table
from DataInterfaceHelper import dataInterfaceHelper
from ExtFinanceInterface import ExtFinanceInterface
import tradingExcpetions as tex
## To use statsmodels for linear regression

## To use sklearn for linear regression


class StockAnalysisHelper(BaseHelper):
    def __init__(self):
        BaseHelper.__init__(self)
    
    dih = dataInterfaceHelper()
    efi=ExtFinanceInterface()

    def topShares(self, marketE, years=3):
        tickers = self.getTickersList(marketE)
        today = datetime.now()
        weekno = datetime.today().weekday()
        today = str(self.holidayDateAdjust(datetime.now() - timedelta(days=1), marketE))
        one_yrs_ago = str(self.holidayDateAdjust(datetime.now() - relativedelta(years=1), marketE))
        two_yrs_ago = str(self.holidayDateAdjust(datetime.now() - relativedelta(years=2), marketE))
        three_yrs_ago = str(self.holidayDateAdjust(datetime.now() - relativedelta(years=3), marketE))
        dates = []
        dates.append(today)
        dates.append(one_yrs_ago)
        dates.append(two_yrs_ago)
        if(years == 3):
            dates.append(three_yrs_ago)
        columns=['ticker','company']
        columns.extend(dates)
        columns.append('yahoo')

        dfNew = pd.DataFrame(
            columns=columns
        )

        for ticker in tickers:
            # so we get the last recorded day info and the year/2 year and then 3 years.
            # if last record close is higher than 1/2/3 years ago then we have a hit.
            # record the ticker name and close values
            sqlStr=""
            todayStr="'"+today+"'"
            one_yrs_agoStr = "'"+one_yrs_ago+"'" 
            two_yrs_agoStr = "'"+two_yrs_ago+"'"
            three_yrs_agoStr="'"+three_yrs_ago+"'"
            
            if(years==3):
                sqlStr="select date,close from "+ ticker.sqlTickerTableStr+ " where date in ({},{},{},{});".format(todayStr, one_yrs_agoStr, two_yrs_agoStr,three_yrs_agoStr
                )
            else:
                sqlStr="select date,close from "+ ticker.sqlTickerTableStr + " where date in ('{}','{}','{}');".format(today, one_yrs_ago, two_yrs_ago)

            df = pd.read_sql_query(sqlStr, self.conn)

            ## look to see if any missing. If so then make another
            if ((years == 3 and df.shape[0] == 4) or (years == 2 and df.shape[0] == 3) ):  # only interested in companies trading for 3 years or more
                if ((years == 3 and
                    (df.iloc[3]["close"] > df.iloc[2]["close"]
                    and df.iloc[2]["close"] > df.iloc[1]["close"]
                    and df.iloc[1]["close"] > df.iloc[0]["close"]))
                    or
                    (years == 2 and
                    (df.iloc[2]["close"] > df.iloc[1]["close"]
                    and df.iloc[1]["close"] > df.iloc[0]["close"]))
                    
                ):
                    df["ticker"] = ticker.tickerStrpName
                    tData,dd=self.efi.getTickerData(ticker,marketE)
                    
                    dfNewLst = [
                        ticker.tickerStrpName,
                        self.get_company_name(ticker,marketE),
                        round(df.iloc[3]["close"],2),
                        round(df.iloc[2]["close"],2),
                        round(df.iloc[1]["close"],2),
                    ]
                    if(years == 3):
                            dfNewLst.append(round(df.iloc[0]["close"],2))
                    dfNewLst.append(dd['yahoo'])
                        

                    dfNew.loc[-1] = dfNewLst # adding a row
                    dfNew.index = dfNew.index + 1  # shifting index
                    dfNew = dfNew.sort_index()  # sorting by index
                    df['id'] = df['ticker']
                    df.set_index('id', inplace=True, drop=False)
            else:
                print("You might need to do a market update for "+ticker.tickerStrpName)
                raise tex.StockOutofDateException

        print(dfNew)
        return dfNew, dates

    def buildDashTable(
        self,
        dff,
        dates,
        marketE,
        height=500,
):
        dates0=dates[0]
        dates1=dates[1]
        dates2=dates[2]
        if(len(dates)==4): 
            dates3=dates[3] 
        else: 
            dates3=""
        return (
            dash_table.DataTable(
                id={"type": "dyn-analysis-table", "index": 0},
                style_as_list_view=True,
                style_cell={
                    "padding": "5px",
                    "textAlign": "left",
                    "fontSize": 13,
                    "font-family": "sans-serif",
                },  # style_cell refers to the whole table
                style_header={
                    "backgroundColor": "white",
                    "fontWeight": "bold",
                    "border": "1px solid black",
                },
                style_data_conditional=[  # style_data.c refers only to data rows
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(248, 248, 248)",
                    },

                    {"if": {"column_id": dates0}, "width": "6%"},
                    {"if": {"column_id": dates1}, "width": "6%"},
                    {"if": {"column_id": dates2}, "width": "6%"},
                    {"if": {"column_id": dates3}, "width": "6%"},
                    {"if": {"column_id": 'yahoo'}, "width": "60%"},
                    {"if": {"column_id": "ticker"}, "width": "6%"},
                    {"if": {"column_id": "company"}, "width": "10%"},
                    {"if": {"column_id": "gross profit"}, "width": "6%"},
                    {"if": {"column_id": "profit margin"}, "width": "7%"},
                    {"if": {"column_id": "cash"}, "width": "6%"},
                    {"if": {"column_id": "debt"}, "width": "6%"},
                    {"if": {"column_id": "forward EPS"}, "width": "6%"},
                    {"if": {"column_id": "Book Val"}, "width": "6%"},
                    {"if": {"column_id": "forward PE"}, "width": "6%"},
                ],
                fixed_rows={"headers": True},
                style_table={"height": height},  # defaults to 500
                data=dff.to_dict("records"),
                style_data={
                    "whiteSpace": "normal",
                    "height": "auto",
                },
                columns=[
                    {"name": i, "id": i, "deletable": False}
                    for i in dff.columns
                    if i != 'id'
                ],
                editable=False,
                # filter_action="native",
                # sort_action="native",
                # sort_mode="multi",
                row_selectable="single",
                # row_deletable=False,
                selected_rows=[],
                column_selectable="single",
                selected_columns=[],
                # page_action="native",
                # page_current=0,
                # page_size=10,
            ),
        )
        css = list(
            list(
                selector=".dash-cell div.dash-cell-value",
                rule="display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;",
            )
        )
        
        def buildPercChangeGraph(self, tickers, marketE):
            tickerPercChangeLst=[]
            for ticker in di.getTickersList(marketE):  
                df=dih.get_historical_data(ticker,str(two_yrs_ago))  
                tickerPercChangeLst.append(di.calculatePecentageChange(df))
                
        
   
    
    
        
        
    
    

        


if __name__ == "__main__":
    di = StockAnalysisHelper()
    #dd = di.topShares(markets_enum.ftse250)
    #print(dd)
 

# %%
