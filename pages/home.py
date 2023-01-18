import dash
from dash import Dash, html, dcc, Output, Input, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

from GraphHelper import GraphHelper
import DataInterfaceHelper
from marketsenum import markets_enum
import logging

di = DataInterfaceHelper.dataInterfaceHelper()

dash.register_page(__name__,  path='/',title="Home")

di.UpdateMarketData(markets_enum.ftse100)
di.UpdateMarketData(markets_enum.ftse250)
di.UpdateMarketData(markets_enum.dow)
di.UpdateMarketData(markets_enum.s_and_p)
di.UpdateMarketData(markets_enum.nasdaq)

layout = html.Div(
    [
        html.H1('Market data', style={'textAlign': 'center'}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4('Date range', style={'textAlign': 'left', "marginLeft": "20px"}),
                        html.Div([dcc.RadioItems(id='date-range',
                                                 options=[dict(label='year to date', value='year to date'),
                                                          dict(label='all available data', value='all available data')],
                                                 labelStyle={'display': 'block'},
                                                 style={
                                                     'fontSize': 20, "marginLeft": "15px", "marginBottom": "20px"},
                                                 inputStyle={
                                                     "marginRight": "20px"},
                                                 value='year to date')]),

                    ], xs=10, sm=10, md=8, lg=4, xl=4, xxl=4
                ),
                dbc.Col(
                    [
                        html.H4('Chart type', style={'textAlign': 'left'}),
                        html.Div([dcc.RadioItems(id='chart-type',
                                                 options=[dict(label='Line', value='line'),
                                                          dict(label='Candle', value='candle')],
                                                 labelStyle={'display': 'block'},
                                                 style={
                                                     'fontSize': 20, "marginLeft": "15px", "marginBottom": "20px"},
                                                 inputStyle={
                                                     "marginRight": "20px"},
                                                 value='line')]),
                    ], xs=10, sm=10, md=8, lg=4, xl=4, xxl=4
                ),
                dbc.Col(html.H4('NEWS', style={'textAlign': 'left', "marginLeft": "20px"}), 
                        xs=10, sm=10, md=8, lg=4, xl=4, xxl=4)
                
            ]
        ),
        dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='ftse100', figure={}, config={'displayModeBar': False},style={'height': '30vh'}),
                ])
            ]),
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='ftse250', figure={}, config={'displayModeBar': False},style={'height': '30vh'}),
                ])
            ]),
        ], width=4),
               dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='dw', figure={}, config={'displayModeBar': False},style={'height': '30vh'}),
                ])
            ]),
        ], width=4),
        ]),
           dbc.Row([
                      dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='sp', figure={}, config={'displayModeBar': False},style={'height': '30vh'}),
                ])
            ]),
        ], width=6),
                          dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='nas', figure={}, config={'displayModeBar': False},style={'height': '30vh'}),
                ])
            ]),
        ], width=6),
           ])
                    
    ])


@callback(
    Output(component_id='ftse100', component_property='figure'),
    Output(component_id='ftse250', component_property='figure'),
    Output(component_id='dw', component_property='figure'),
    Output(component_id='sp', component_property='figure'),
    Output(component_id='nas', component_property='figure'),
    Input(component_id='date-range', component_property='value'),
    Input(component_id='chart-type', component_property='value')
)
# represents that which is assigned to the component property of the Input
def build_graphs(chosen_date_range, chosen_chart_type):
    df_ftse100 = di.get_marketData(markets_enum.ftse100, chosen_date_range)
    df_ftse250 = di.get_marketData(markets_enum.ftse250, chosen_date_range)
    df_dow = di.get_marketData(markets_enum.dow, chosen_date_range)
    df_s_p = di.get_marketData(markets_enum.s_and_p, chosen_date_range)
    df_nasdaq=di.get_marketData(markets_enum.nasdaq,chosen_date_range)
    
    ftse100StartVal,ftse100EndVal=di.getMarketCurrentValue(markets_enum.ftse100)
    ftse250StartVal,ftse250EndVal=di.getMarketCurrentValue(markets_enum.ftse250)
    dowStartVal,dowEndVal=di.getMarketCurrentValue(markets_enum.dow)
    s_pStartVal,s_pEndVal=di.getMarketCurrentValue(markets_enum.s_and_p)
    nasdaqStartVal,nasdaqEndVal=di.getMarketCurrentValue(markets_enum.nasdaq)
     
    gh = GraphHelper()
    ftse100g = gh.getGraph(df_ftse100, "FTSE 100", "pence", ftse100StartVal,
                           ftse100EndVal, chosen_chart_type)
    ftse250g = gh.getGraph(df_ftse250, "FTSE 250", "pence", ftse250StartVal,
                           ftse250EndVal, chosen_chart_type)
    dowg = gh.getGraph(df_dow, "Dow", "$", dowStartVal,dowEndVal,chosen_chart_type)
    spg = gh.getGraph(df_s_p, "S&P", "$", s_pStartVal,s_pEndVal,chosen_chart_type)
    nasg= gh.getGraph(df_nasdaq, "NASDAQ", "$",nasdaqStartVal,nasdaqEndVal, 
                      chosen_chart_type)

    # xaxis_rangeslider_visible=False,
    ftse100g.update_layout(margin=dict(t=50, b=5, l=2, r=2))
    ftse250g.update_layout(margin=dict(t=50, b=5, l=2, r=2))
    dowg.update_layout(margin=dict(t=30, b=5, l=2, r=2))
    spg.update_layout(margin=dict(t=30, b=5, l=2, r=2))
    nasg.update_layout(margin=dict(t=30, b=5, l=2, r=2))
    return ftse100g, ftse250g, dowg, spg, nasg


# if __name__ == '__main__':
#     app.run_server(port=8051)
