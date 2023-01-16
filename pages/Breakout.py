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
from CandelstickAnalHelper import CandlestickAnalHelper

dash.register_page(__name__, order=7)

dih = dataInterfaceHelper()
ca=CandlestickAnalHelper()

layout = html.Div(
    [
        html.H1('Breakout', style={'textAlign': 'center'}),
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown(id='markets', placeholder='market...',
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
                        width={'size': 3}
                        ),
                dbc.Col(dcc.Dropdown(id='chart_type', placeholder='chart type',
                                     options=[
                                        {'label': 'candle', 'value': 'candle'},
                                        {'label': 'ohlc', 'value': 'ohlc'},
                                        {'label': 'line', 'value': 'line'},
                                        {'label': 'renko', 'value': 'renko'},
                                        {'label': 'pnf', 'value': 'pnf'}
                                     ]),
                        width={'size': 2}),
                                dbc.Col(dcc.Input(id="bper", type="number",placeholder="Breakout %"),
                        width={'size': 2,}),
                dbc.Col(
                        dcc.Input(id="bnodays", type="number", placeholder="Breakout number of days"),
                        width={'size': 2 }
                ),
                dbc.Col(
                    [
                    html.Div(id='cons_div'),
                    
                    ],width={'size': 2, 'offset': 1}
                )
            ]
        ),
        dbc.Row([
            dbc.Col(
                [
                    html.Div(id='dyn-comp-gr')                    
                ], width=6
            ),

        ])

    ])


@callback(
    Output('cons_div', 'children'),
    Output('dyn-comp-gr', 'children'),
    Input(component_id='markets', component_property='value')
)
def build_market_data(marketVal):
    if (marketVal != None):
        tickers =ca.consolidating(markets_enum[marketVal],5,10) 
        dd=dcc.Dropdown(
            id={
                'type': 'dynamic-comp-lst',
                'index': 0,
            }, placeholder='Market',
            options=tickers)
        graph=dcc.Graph(
                id={
                    'type': 'dynamic-graph2',
                    'index': 0
                },
                figure={}
            )
        #tab=buildTable()
        return dd,graph
                
    else:
        raise PreventUpdate


@callback(
    Output({'type': 'dynamic-graph2', 'index': MATCH}, 'figure'),
    Input(component_id='markets', component_property='value'),
    Input(component_id='chart_type', component_property='value'),
    Input(component_id='bper', component_property='value'),
    Input(component_id='bnodays', component_property='value'),
    Input(component_id={'type': 'dynamic-comp-lst', 'index': MATCH}, component_property='value'), 
    prevent_initial_call=True
    
)
# def buildCompData(marketVal, chartVal, bperVal, days, compVar):
#     print("compVar "+str(compVar))
#     raise PreventUpdate

#def buildCompData(marketVal, chartVal, dateVal, ticker):
def buildCompData(marketVal, chartType, bperVal, days, compVar):
    if compVar is None:
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate
    if(compVar is not None):
        df = ca.breakout(compVar, days)
        gh = GraphHelper()
        gr=gh.getGraph(df,compVar,"£", 0.0,0.0,chartType)
        gr.update_layout(margin=dict(t=100, b=5, l=2, r=2),width=1200, height=500)
                
        return gr
    else:
        raise PreventUpdate

   