import dash
from dash import Dash, html, dcc, Output, Input, callback
import dash_bootstrap_components as dbc
from marketsenum import markets_enum
from CandelstickAnalHelper import CandlestickAnalHelper


dash.register_page(__name__, title="Breakouts", order=3)
ca=CandlestickAnalHelper()

def buildConsList(conList):
    if(len(conList)==0):
        return ""
    theList=[]
    for con in conList:
        theList.append({con:con})
        
    dcc.Dropdown(id='br_style', placeholder='breakout style',
                                     options=theList),

dropdownOptions = [
    {'label': 'default', 'value': 'default'},
    {'label': 'binance', 'value': 'binance'},
    {'label': 'blueskies', 'value': 'blueskies'},
    {'label': 'brasil', 'value': 'brasil'},
    {'label': 'charles', 'value': 'charles'},
    {'label': 'checkers', 'value': 'checkers'},
    {'label': 'classic', 'value': 'classic'},
    {'label': 'yahoo', 'value': 'yahoo'},
    {'label': 'mike', 'value': 'mike'},
    {'label': 'nightclouds', 'value': 'nightclouds'},
    {'label': 'sas', 'value': 'sas'},
    {'label': 'starsandstripes', 'value': 'starsandstripes'}
]


layout = html.Div(
    [
        html.H1('Breakout analysis', style={'textAlign': 'center'}),
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown(id='markets', placeholder='Market',
                                     options=[{'label': 'FTSE 100', 'value': 'FTSE100'},
                                              {'label': 'FTSE 250',
                                               'value': 'FTSE250'},
                                              {'label': 'DOW', 'value': 'DOW'},
                                              {'label': 'NASDAQ', 'value': 'NASDAQ'}]),
                        width={'size': 2, 'offset':1}
                        ),
                dbc.Col(dcc.Dropdown(id='br_style', placeholder='breakout style',
                                     options=dropdownOptions),
                        width={'size': 2}
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
            ]
        ),
        dbc.Row(
            [
                html.Div(id='break_selec'),
            ])

    ])


@callback(
    Output('break_selec', 'children'),
    Input(component_id='market_dropdown', component_property='value'),
    Input(component_id='br_style', component_property='value'),
    Input(component_id='chart_type', component_property='value'),
    Input(component_id='bper', component_property='value'),
    Input(component_id='bnodays', component_property='value'), prevent_initial_call=True
)
def build_graphs(marketVal, breakoutStyle, chartType, breakPerc, breakDays):
    if(marketVal != None):
       consolidated_list =ca.consolidating(markets_enum.ftse100,breakPerc,breakDays) 
       return(buildConsList(consolidated_list))
