import numpy as np
import dash
from dash import Dash, html, dcc, Output, Input, callback, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from patterns import candlestick_patterns, candlestick_patterns_urls
from DataInterfaceHelper import dataInterfaceHelper

from GraphHelper import GraphHelper
from CandelstickAnalHelper import CandlestickAnalHelper
from marketsenum import markets_enum
from dash.exceptions import PreventUpdate

import datetime
from dateutil.relativedelta import relativedelta
import talib

breakout_perc = 2
breakout_trading_range = 16
breakout = "None"
cah = CandlestickAnalHelper()

chart_styles = [
    'default', 'binance', 'blueskies', 'brasil',
    'charles', 'checkers', 'classic', 'yahoo',
    'mike', 'nightclouds', 'sas', 'starsandstripes'
]




dash.register_page(__name__,  title="Candlestick analysis", order=4)

layout = html.Div(
    [
        html.Br(),
        html.H1('Breakout analysis', style={'textAlign': 'center'}),
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown(id='market_dropdown', placeholder='Market',
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
                            ]),
                        width={'size': 3}
                        ),
                dbc.Col(dcc.Dropdown(id='candlestick_pat', placeholder='candlestick patterns',
                                     options=candlestick_patterns),
                        width={'size': 2}
                        ), 
                dbc.Col(html.Div(id='candlestickURLBut'))         
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Spinner(html.Div(id="candlestick_anal"),spinner_style={"width": "3rem", "height": "3rem"}),
                    #html.Div(id='candlestick_anal'),width={'size': 8}
                    width={'size': 8})
            ])

    ])

@callback(
    Output('candlestickURLBut', 'children'),
    Input(component_id='candlestick_pat', component_property='value'),
   prevent_initial_call=True
)
def buildURL(candlestickVal):
    if(candlestickVal != None):
        di = dataInterfaceHelper() 
        val = [v for k, v in candlestick_patterns.items() if k == candlestickVal][0]
        return html.A(val, href=candlestick_patterns_urls[candlestickVal], target="_blank")              
    else:
        raise PreventUpdate
    
@callback(
    Output('candlestick_anal', 'children'),
    Input(component_id='market_dropdown', component_property='value'),
    Input(component_id='candlestick_pat', component_property='value'),
    [State('candlestick_anal', 'children')],
)
def procCandlestick(marketVal, candlestickVal, children):
    di = dataInterfaceHelper()
    if children == None:
        children=[]
    if(marketVal != None and candlestickVal != None):
        tickers = di.get_stocks_list(markets_enum[marketVal])
        pattern_function = getattr(talib, candlestickVal)

        for tickerNames in tickers:
            try:
                df = di.get_ticker_data(tickerNames.tickerStrpName)
                descTxt,fig=cah.buildFigureAndDescTxt(markets_enum[marketVal],tickerNames,df,pattern_function)
                if(fig==None):
                    continue
                children.append(html.Div(descTxt))
                children.append(dcc.Graph(figure=fig,style={'width': '90vh', 'height': '90vh'}))
            except Exception as e:
                print(str(e))
        return children         
    else:
        raise PreventUpdate
