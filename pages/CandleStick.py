import dash
from dash import Dash, html, dcc, Output, Input, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from patterns import candlestick_patterns, candlestick_patterns_urls

from GraphHelper import GraphHelper
from CandelstickAnalHelper import CandlestickAnalHelper
from marketsenum import markets_enum

breakout_perc = 2
breakout_trading_range = 16
breakout = "None"
ca = CandlestickAnalHelper()

chart_styles = [
    'default', 'binance', 'blueskies', 'brasil',
    'charles', 'checkers', 'classic', 'yahoo',
    'mike', 'nightclouds', 'sas', 'starsandstripes'
]

dash.register_page(__name__,  title="Candlestick analysis", order=4)

layout = html.Div(
    [
        html.H1('Breakout analysis', style={'textAlign': 'center'}),
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown(id='market_dropdown', placeholder='Market',
                                     options=[{'label': 'FTSE 100', 'value': 'FTSE100'},
                                              {'label': 'FTSE 250',
                                               'value': 'FTSE250'},
                                              {'label': 'DOW', 'value': 'DOW'},
                                              {'label': 'NASDAQ', 'value': 'NASDAQ'}]),
                        width={'size': 4, "offset": 1, 'order': 1}
                        ),
                dbc.Col(dcc.Dropdown(id='can_pat', placeholder='candlestick patterns',
                                     options=candlestick_patterns),
                        width={'size': 4, "offset": 1, 'order': 1}
                        ),          
            ]
        ),
        dbc.Row(
            [
                html.Div(id='break_selec'),
            ])

    ])
