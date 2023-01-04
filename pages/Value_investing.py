import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash import html, dcc
from dash import Dash, Input, Output, callback, dcc, html, ctx, State
from dash.exceptions import PreventUpdate
from ValueInvestingHelper import ValueInvestingHelper
from marketsenum import markets_enum

dash.register_page(__name__, title="Value Investing",order=6)

layout = html.Div(
    [
        html.H1('Value Investing', style={'textAlign': 'center'}),
        
        dbc.Row(
                [
                    dbc.Col(width={'size': 1}),
                    dbc.Col([
                       dcc.Dropdown(id='markets', placeholder='market...',
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
                                    'value': 'nasdaq_Utilities'}]
                                ),
                        html.Br(),
                        dbc.Button("Review", id="review-btn", className="me-2", n_clicks=0),
                        dbc.Button("Update", id="update-btn", className="me-2", n_clicks=0),
                        ],width={'size': 9}),
                    dbc.Col([

                        ],
                        width={'size': 1})
                ],
        ),        
                                    
                # dbc.Col(
                #     [
                #     html.Div(id='cons_div'),
                    
                #     ],width={'size': 2, 'offset': 1}
                # )
        dbc.Row([
            dbc.Col(
                [
                     dbc.Spinner(html.Div(id="val-inv-output"),spinner_style={"width": "3rem", "height": "3rem"}),                   
                ], width=6
            ),

         ])

    ])

@callback(
    Output(component_id='val-inv-output', component_property='children'),
    State(component_id='markets', component_property='value'),
    Input(component_id="review-btn", component_property='n_clicks'),
    Input(component_id="update-btn", component_property='n_clicks'),
)
def build_market_data(marketVal, reviewBtn, updateBtn):
    vih = ValueInvestingHelper()
    
    if (marketVal == None):
        raise PreventUpdate
    marketE=markets_enum[marketVal.lower()]
    if "review-btn" == ctx.triggered_id:
        vih.processData(marketE)
        tickers = vih.finalResults()
        
    if "update-btn" == ctx.triggered_id:
        vih.financialInfo(marketE)   
        