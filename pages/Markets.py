import dash
import dash_bootstrap_components as dbc
from DataInterfaceHelper import dataInterfaceHelper
from marketsenum import markets_enum
from datetime import date, timedelta
from GraphHelper import GraphHelper
from dash import Input, MATCH, Output, callback, dcc, html
from dash.exceptions import PreventUpdate
import logging
from UIHelper import UIHelper
import pageNames

dash.register_page(__name__, order=pageNames.pn['markets'])

dih = dataInterfaceHelper()

layout = html.Div(
    [
        html.H1('Company data', style={'textAlign': 'center'}),
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown(id='markets-mar', placeholder='Market',
                                     options=[{'label': 'FTSE 100', 'value': 'ftse100'},
                                              {'label': 'FTSE 250',
                                               'value': 'ftse250'},
                                              {'label': 'DOW', 'value': 'dow'},
                                              {'label': 'NASDAQ', 'value': 'nasdaq'}]),
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
                ], width=6
            )
        ])

    ])


@callback(
    Output('markets_div', 'children'),
    Output('dynamic-comp-gr', 'children'),
    Input(component_id='markets-mar', component_property='value')
)
def build_market_data(marketVal):
    uiHelper=UIHelper()
    if (marketVal != None):
        dd=uiHelper.companyNameDropDown(markets_enum[marketVal.lower()], 'dynamic-comp-lst')
        graph=dcc.Graph(
                id={
                    'type': 'dynamic-graph',
                    'index': 0
                },
                figure={}
            )
        return dd,graph
                
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
    if(ticker is not None):
        currency=None
        marketE=markets_enum[marketVal.lower()]
        symbol = dih.get_compound_ticker_name(ticker, marketE)
        if(marketE == markets_enum.ftse100 or marketE == markets_enum.ftse250):
            currency="£"
        else:
            currency="$"
        compName=dih.get_company_name(symbol, marketE)+"("+ticker+")"
        data = dih.get_historical_data(symbol, dateVal)
        gh = GraphHelper()
        gr=gh.getGraph(data,compName,currency, 0.0,0.0,chartVal)
        gr.update_layout(margin=dict(t=50, b=5, l=2, r=2))
               
        tData=dih.getTickerData(symbol)
        tb=gh.buildTable(tData)
        ht=html.Div(tb)
        
        return gr,ht
    else:
        raise PreventUpdate

   