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
#from dash.long_callback import DiskcacheLongCallbackManager
import pageNames

app = Dash(__name__)

dash.register_page(__name__,  title="Stock performance", order=pageNames.pn['stock_performance'])

# select market
# by selecting market will pre-populate company dropdown
# select comany will display graph and current business data
# <<NEXT VERSION >> plot many selected companies
# plot ftse100, dow etc in plot.
# display news


layout = html.Div(
    [
        html.H1('Stock Performance', style={'textAlign': 'center'}),
        html.Br(),
 
        dbc.Row(
            [
                    html.Div(
                    dcc.Dropdown(id='markets-mar2', placeholder='market...',
                        options=[{'label': 'FTSE 100', 'value': 'ftse100'},
                                {'label': 'FTSE 250', 'value': 'ftse250'},
                                {'label': 'DOW', 'value': 'dow'},
                                {'label': 'NASDAQ-Basic Materials',
                                    'value': 'nasdaq_BasicMaterials'},
                                {'label': 'NASDAQ-Consumer Discretionary',
                                    'value': 'nasdaq_ConsumerDiscretionary'},
                                {'label': 'NASDAQ-Consumer Staples',
                                    'value': 'nasdaq_ConsumerStaples'},
                                {'label': 'NASDAQ-Energy',
                                    'value': 'nasdaq_Energy'},
                                {'label': 'NASDAQ-Finance',
                                    'value': 'nasdaq_Finance'},
                                {'label': 'NASDAQ-Health Care',
                                    'value': 'nasdaq_HealthCare'},
                                {'label': 'NASDAQ-Industrials',
                                    'value': 'nasdaq_Industrials'},
                                {'label': 'NASDAQ-Miscellaneous',
                                    'value': 'nasdaq_Miscellaneous'},
                                {'label': 'NASDAQ-Real Estate',
                                    'value': 'nasdaq_RealEstate'},
                                {'label': 'NASDAQ-Technology',
                                    'value': 'nasdaq_Technology'},
                                {'label': 'NASDAQ-Telecommunications',
                                    'value': 'nasdaq_Telecommunications'},
                                {'label': 'NASDAQ-Utilities',
                                    'value': 'nasdaq_Utilities'},
                            ]
                        ),
                        style={'marginBottom': 50, 'marginTop': 50, 'width':'40%'}
                    ),
                 dbc.Spinner(html.Div(id="loading-output2"),spinner_style={"width": "3rem", "height": "3rem"}),
            ]),
    ])