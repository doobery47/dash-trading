from marketsenum import markets_enum
import pandas as pd
from DataBaseHelper import DataBaseHelper
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas
import holidays
from dash import dash_table
from DataInterfaceHelper import dataInterfaceHelper


class StockAnalysisHelper(DataBaseHelper):
    def __init__(self):
        DataBaseHelper.__init__(self)

    def dateMove(self, dat, marketE):
        if dat.weekday() > 4:
            dat = dat - timedelta(
                days=dat.weekday() - 4
            )  # move sat or sunday to firday
        else:
            if marketE == markets_enum.ftse100 or marketE == markets_enum.ftse250:
                this_holiday = holidays.UK()
            else:
                this_holiday = holidays.US()

            if dat in this_holiday:
                dat = dat - timedelta(days=1)
                self.dateMove(dat, marketE)
        return str(dat.date())

    def topShares(self, marketE, years=3):
        tickers = self.get_stocks_list(marketE)
        today = datetime.now()
        weekno = datetime.today().weekday()
        # fri=4
        # sat=5#
        # sun=6
        today = self.dateMove(datetime.now() - timedelta(days=1), marketE)
        one_yrs_ago = self.dateMove(datetime.now() - relativedelta(years=1), marketE)
        two_yrs_ago = self.dateMove(datetime.now() - relativedelta(years=2), marketE)
        three_yrs_ago = self.dateMove(datetime.now() - relativedelta(years=3), marketE)
        dates = []
        dates.append(today)
        dates.append(one_yrs_ago)
        dates.append(two_yrs_ago)
        dates.append(three_yrs_ago)

        dfNew = pd.DataFrame(
            columns=[
                "ticker",
                "company",
                str(three_yrs_ago),
                str(two_yrs_ago),
                str(one_yrs_ago),
                str(today),
                "sector",
                "gross profit",
                "profit margin",
                "cash",
                "debt",
                "forward EPS",
                "Book Val",
                "forward PE",
            ]
        )

        for ticker in tickers:
            # so we get the last recorded day info and the year/2 year and then 3 years.
            # if last record close is higher than 1/2/3 years ago then we have a hit.
            # record the ticker name and close values
            dih = dataInterfaceHelper()

            df = pd.read_sql_query(
                "select date,close from "
                + ticker.sqlTickerTableStr
                + " where date in ('{}','{}','{}','{}');".format(
                    today, one_yrs_ago, two_yrs_ago,three_yrs_ago
                ),
                self.conn,
            )
            ## look to see if any missing. If so then make another
            if (
                df.shape[0] == 4
            ):  # only interested in companies trading for 3 years or more
                if (
                    df.iloc[3]["close"] > df.iloc[2]["close"]
                    and df.iloc[2]["close"] > df.iloc[1]["close"]
                    and df.iloc[1]["close"] > df.iloc[0]["close"]
                ):
                    df["ticker"] = ticker.tickerStrpName
                    tData,dd=dih.getTickerDataTest(ticker)

                    dfNew.loc[-1] = [
                        ticker.tickerStrpName,
                        self.get_company_name(ticker,marketE),
                        df.iloc[0]["close"],
                        df.iloc[1]["close"],
                        df.iloc[2]["close"],
                        df.iloc[3]["close"],
                        dd["sector"],
                        dd["gross profits"],
                        dd["profit margins"],
                        dd["total cash"],
                        dd["total debt"],
                        dd["forward EPS"],
                        dd["book value"],
                        dd["forward PE"],
                    ]  # adding a row
                    dfNew.index = dfNew.index + 1  # shifting index
                    dfNew = dfNew.sort_index()  # sorting by index
                    df['id'] = df['ticker']
                    df.set_index('id', inplace=True, drop=False)

        print(dfNew)
        return dfNew, dates

    def buildDashTable(
        self,
        dff,
        dates,
        marketE,
        height=500,
    ):
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
                # tooltip_data=[{
                #     'ticker': {
                #         'value': self.get_company_name(self.get_compound_ticker_name(row['ticker'],marketE),marketE),
                #         'type': 'markdown'
                #     }
                # } for row in dff.to_dict('records')],
                # ----------------------------------------------------------------
                # Striped Rows
                # ----------------------------------------------------------------
                # style_header={
                #     'backgroundColor': 'rgb(230, 230, 230)',
                #     'fontWeight': 'bold'
                # },
                style_data_conditional=[  # style_data.c refers only to data rows
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(248, 248, 248)",
                    },
                    {"if": {"column_id": dates[0]}, "width": "6%"},
                    {"if": {"column_id": dates[1]}, "width": "6%"},
                    {"if": {"column_id": dates[2]}, "width": "6%"},
                    {"if": {"column_id": dates[3]}, "width": "6%"},
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


if __name__ == "__main__":
    di = StockAnalysisHelper()
    dd = di.topShares(markets_enum.ftse250)
    print(dd)
