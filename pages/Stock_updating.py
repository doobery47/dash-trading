import dash
import dash_bootstrap_components as dbc
from DataInterfaceHelper import dataInterfaceHelper
from marketsenum import markets_enum
from datetime import date, timedelta
from GraphHelper import GraphHelper
from dash import Dash, html, dcc, Output, Input, callback, State, MATCH
from marketsenum import markets_enum
from CandelstickAnalHelper import CandlestickAnalHelper
from dash.exceptions import PreventUpdate
from dash import dash_table
import pandas as pd
from StockUpdateHelper import StockUpdateHelper

dash.register_page(__name__,  title="Stock Updates", order=7)

layout = html.Div(
    [
        html.H1('Breakout analysis', style={'textAlign': 'center'}),
        dbc.Row([
            dbc.Col(
                [
                    dcc.Interval(
                        id="load_interval",
                        n_intervals=0,
                        max_intervals=0,  # <-- only run once
                        interval=1
                    ),
                    html.Div(id='markets_status')
                ], width=6
            ),

        ]),
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown(id='markets-mar', placeholder='Market',
                    options=[{'label': 'FTSE 100', 'value': 'ftse100'},
                            {'label': 'FTSE 250',
                                'value': 'ftse250'},
                            {'label': 'DOW', 'value': 'dow'},
                            {'label': 'NASDAQ-Basic Materials',
                                'value': 'nasdaq-Basic Materials'},
                            {'label': 'NASDAQ-Consumer Discretionary',
                                'value': 'nasdaq-Consumer Discretionary'},
                            {'label': 'NASDAQ-Consumer Staples',
                                'value': 'nasdaq-Consumer Staples'},
                            {'label': 'NASDAQ-Energy',
                                'value': 'nasdaq-Energy'},
                            {'label': 'NASDAQ-Finance',
                                'value': 'nasdaq-Finance'},
                            {'label': 'NASDAQ-Health Care',
                                'value': 'nasdaq-Health Care'},
                            {'label': 'NASDAQ-Industrials',
                                'value': 'nasdaq-Industrials'},
                            {'label': 'NASDAQ-Miscellaneous',
                                'value': 'nasdaq-Miscellaneous'},
                            {'label': 'NASDAQ-Real Estate',
                                'value': 'nasdaq-RealEstate'},
                            {'label': 'NASDAQ-Technology',
                                'value': 'nasdaq-Technology'},
                            {'label': 'NASDAQ-Telecommunications',
                                'value': 'nasdaq-Telecommunications'},
                            {'label': 'NASDAQ-Utilities',
                                'value': 'nasdaq-Utilities'},

                            ]),
                        width={'size': 2, 'offset': 1}
                        ),
            ]),


    ])


@callback(
    Output('markets_status', 'children'),
    Input(component_id="load_interval", component_property="n_intervals"),
)
def statusList(n_intervals: int):
    suh = StockUpdateHelper()
    gh = GraphHelper()
    tdf = suh.getMarketStatus()
    return gh.buildTable(tdf, height=300)


@callback(
    Output('markets_div', 'children'),
    Input(component_id='markets-mar', component_property='value')
)
def build_market_data(marketVal):
    di = dataInterfaceHelper()
    ticker_list = di.get_stocks_list(marketVal)

#     data = []
#     if(ticker_list):
#         progress_inc = 100/len(ticker_list)
#         counter=0
#         dfStatus = pd.DataFrame(columns=["Ticker","Status"])


#         for ticker in ticker_list:
#             try:
#                 status=di.updateHistoryDataFTSE(ticker)
#                 dfStatus = dfStatus.append({'Ticker': ticker.tickerStrpName, 'Status':status}, ignore_index=True)
#                 print(len(dfStatus))


#             except Exception as e:
#                 data.append([ticker.ticker,repr(e)])
#             counter = counter + progress_inc
#             if(counter >100):
#                 counter = 100
#             my_bar.progress(math.ceil(counter))

#         if(data):
#             df = pd.DataFrame(data, columns=['Ticker', 'Error'])
#             st.table(df)

#         st.success('Done!')


#         else:
#             raise PreventUpdate
