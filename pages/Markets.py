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


    

dash.register_page(__name__, order=5)

dih = dataInterfaceHelper()

dash.register_page(__name__, order=5)

layout = html.Div(
    [
        html.H1('Breakout analysis', style={'textAlign': 'center'}),
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown(id='markets-mar', placeholder='Market',
                                     options=[{'label': 'FTSE 100', 'value': 'FTSE100'},
                                              {'label': 'FTSE 250',
                                               'value': 'FTSE250'},
                                              {'label': 'DOW', 'value': 'DOW'},
                                              {'label': 'NASDAQ', 'value': 'NASDAQ'}]),
                        width={'size': 2, 'offset': 1}
                        ),
                dbc.Col(
                    [
                        html.H4('Chart type', style={'textAlign': 'left'}),
                        html.Div([dcc.RadioItems(id='chart-type_mar',
                                                 options=[dict(label='Line', value='line'),
                                                          dict(label='Candle', value='candle')],
                                                 labelStyle={
                                                     'display': 'block'},
                                                 style={
                                                     'fontSize': 20, "marginLeft": "15px", "marginBottom": "20px"},
                                                 inputStyle={
                                                     "marginRight": "20px"},
                                                 value='line')]),
                    ], xs=10, sm=10, md=8, lg=4, xl=4, xxl=4
                ),
                dbc.Col(
                    [
                        dcc.DatePickerSingle(
                            id='my-date-picker-single',
                            min_date_allowed=date.today() + timedelta(days=-364),
                            max_date_allowed=date.today(),
                            initial_visible_month=date.today() + timedelta(days=-364),
                            date=date.today() + timedelta(days=-364)
                        ),
                        html.Div(id='output-container-date-picker-single')
                    ]
                ),
                dbc.Col(
                    [
                    html.Div(id='markets_div'),
                    
                    ],width={'size': 2, 'offset': 1}
                )
            ]
        ),
        dbc.Row([
            dbc.Col(
                [
                    html.Div(id='dynamic-comp-gr')                    
                ], width=6
            ),
            dbc.Col(
            [
                    html.Div(id={
                    'type': 'dynamic-tab',
                    'index': 0
                })                    
                ], width=5
            )
        ])

    ])


@callback(
    Output('markets_div', 'children'),
    Output('dynamic-comp-gr', 'children'),
    Input(component_id='markets-mar', component_property='value')
)
def build_market_data(marketVal):
    if (marketVal != None):
        tickers = dih.get_stock_list_names(markets_enum[marketVal.lower()])
        dd=dcc.Dropdown(
            id={
                'type': 'dynamic-comp-lst',
                'index': 0,
            }, placeholder='Market',
            options=tickers)
        graph=dcc.Graph(
                id={
                    'type': 'dynamic-graph',
                    'index': 0
                },
                figure={}
            )
        #tab=buildTable()
        return dd,graph#,tab
                
    else:
        raise PreventUpdate


@callback(
    Output('output-container-date-picker-single', 'children'),
    Input('my-date-picker-single', 'date'))
def update_output(date_value):
    string_prefix = 'You have selected: '
    if date_value is not None:
        date_object = date.fromisoformat(date_value)
        date_string = date_object.strftime('%B %d, %Y')
        return string_prefix + date_string


@callback(
    Output({'type': 'dynamic-graph', 'index': MATCH}, 'figure'),
    Output({'type': 'dynamic-tab', 'index': MATCH}, 'children'),
    Input(component_id='markets-mar', component_property='value'),
    Input(component_id='chart-type_mar', component_property='value'),
    Input(component_id='my-date-picker-single', component_property='date'),
    Input(component_id={'type': 'dynamic-comp-lst', 'index': MATCH}, component_property='value'), 
    prevent_initial_call=True
)
def buildCompData(marketVal, chartVal, dateVal, ticker):
    if ticker is None:
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate
    print("here")
    if(ticker is not None):
        currency=None
        marketE=markets_enum[marketVal.lower()]
        symbol = dih.get_compound_stock_name(ticker, marketE)
        if(marketE == markets_enum.ftse100 or marketE == markets_enum.ftse250):
            currency="£"
        else:
            currency="$"
        compName=dih.get_company_name(symbol, marketE)
        data = dih.get_historical_data(symbol, str(dateVal), True)
        gh = GraphHelper()
        gr=gh.getGraph(data,compName,currency, 0.0,0.0,chartVal)
        gr.update_layout(margin=dict(t=50, b=5, l=2, r=2))
               
        tData=dih.getTickerData(symbol, marketE)
        tb=gh.buildTable(tData)
        ht=html.Div(tb)
        
        return gr,ht
    else:
        raise PreventUpdate

   