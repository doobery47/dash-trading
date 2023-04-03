import dash
import dash_bootstrap_components as dbc
from DataInterfaceHelper import dataInterfaceHelper
from marketsenum import markets_enum
from GraphHelper import GraphHelper
from dash import Dash, Input, Output, callback, dcc, html
from marketsenum import markets_enum
import pandas as pd
from StockUpdateHelper import StockUpdateHelper
import logging
import pageNames
#from dash.long_callback import DiskcacheLongCallbackManager


app = Dash(__name__)

dash.register_page(__name__,  title="Stock Updates", order=pageNames.pn['stock_updating'])

def startList():
    suh=StockUpdateHelper()
    gh=GraphHelper()
    tdf=suh.getMarketStatus()
    return gh.buildDashTable(tdf, height=300)

## Diskcache
# import diskcache
# cache = diskcache.Cache("./cache")
# long_callback_manager = DiskcacheLongCallbackManager(cache)

layout = html.Div(
    [
        html.H1('Stock Updates', style={'textAlign': 'center'}),
        html.Br(),
        dbc.Row([
            dbc.Col(
                [
                    dcc.Interval(
                        id="load_interval",
                        n_intervals=0,
                        max_intervals=0,  # <-- only run once
                        interval=1
                    ),
                   html.Div(id='table'),
                            #html.Div(id='markets_status')
                ], width=6
            ),

        ]),
        dbc.Row(
            [
                    html.Div(
                    dcc.Dropdown(id='markets-mar', placeholder='Update market...',
                        options=[{'label': 'FTSE 100', 'value': 'ftse100'},
                                 {'label': 'All markets', 'value': 'all'},
                                {'label': 'FTSE 250', 'value': 'ftse250'},
                                {'label': 'DOW', 'value': 'dow'},
                                {'label': 'All nasdaq', 'value': 'all_nasdaq'},
                                {'label': 'NASDAQ-Basic Materials',
                                    'value': 'nasdaq_basic_materials'},
                                {'label': 'NASDAQ-Consumer Discretionary',
                                    'value': 'nasdaq_consumer_discretionary'},
                                {'label': 'NASDAQ-Consumer Staples',
                                    'value': 'nasdaq_consumer_staples'},
                                {'label': 'NASDAQ-Energy',
                                    'value': 'nasdaq_energy'},
                                {'label': 'NASDAQ-Finance',
                                    'value': 'nasdaq_finance'},
                                {'label': 'NASDAQ-Health Care',
                                    'value': 'nasdaq_health_care'},
                                {'label': 'NASDAQ-Industrials',
                                    'value': 'nasdaq_industrials'},
                                {'label': 'NASDAQ-Miscellaneous',
                                    'value': 'nasdaq_miscellaneous'},
                                {'label': 'NASDAQ-Real Estate',
                                    'value': 'nasdaq_realestate'},
                                {'label': 'NASDAQ-Technology',
                                    'value': 'nasdaq_technology'},
                                {'label': 'NASDAQ-Telecommunications',
                                    'value': 'nasdaq_telecommunications'},
                                {'label': 'NASDAQ-Utilities',
                                    'value': 'nasdaq_utilities'},
                            ]
                        ),
                        style={'marginBottom': 50, 'marginTop': 50, 'width':'40%'}
                    ),
                 dbc.Spinner(html.Div(id="loading-output"),spinner_style={"width": "3rem", "height": "3rem"}),
            ]),
    ])

# 1. display the last updates for each of the markets (nasdaq broken down into sectors)
# 2 User selects market from drop down.
# 3. Initiation starts for the update
# 4. The interval is started (output) for the status of the update
# 5. Make a call to see how many have been updated. Output should be the total number of tickers plus the number that
#    has been processed so far.
# 6. Update the progress bar
# 7. Once the processed so far = total number of tickers then the user is informed that it is finished and the
#    progress bar is stoppped


@callback(
    Output(component_id='table', component_property='children'),
    Output(component_id='loading-output', component_property='children'),
    Input(component_id="load_interval", component_property="n_intervals"),
    Input(component_id='markets-mar', component_property='value'),
)
def build_market_data(n_intervals: int,marketVal):
    if(marketVal != None): 
        di=dataInterfaceHelper()
        suh=StockUpdateHelper()
        gh=GraphHelper()
        marketValE=markets_enum[marketVal]
        ticker_list=di.getTickersList(marketValE)

        data=[]
        if (ticker_list):
            dfStatus=pd.DataFrame(columns=["Ticker", "Status"])
            for ticker in ticker_list:
                try:
                    status=di.updateHistoryDataForTicker(ticker,marketValE)
                except Exception as e:
                    data.append([ticker.ticker, repr(e)])                    
            suh=StockUpdateHelper()
            dff=suh.getMarketStatus()
            # data=dff.to_dict('records')
            return dbc.Table.from_dataframe(dff,striped=True, bordered=True, hover=True,
                                            size='sm'),marketVal+" completed updatiing"
    else:
        suh=StockUpdateHelper()
        dff=suh.getMarketStatus()
        # data=dff.to_dict('records')
        return dbc.Table.from_dataframe(dff,striped=True, bordered=True, hover=True, size='sm'),""
        
