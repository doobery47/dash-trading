import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash import html, dcc
from dash import Dash, Input, Output, callback, dcc, html, ctx, State
from dash.exceptions import PreventUpdate
from ValueInvestingHelper import ValueInvestingHelper
from marketsenum import markets_enum
from GraphHelper import GraphHelper
from DataInterfaceHelper import dataInterfaceHelper
import logging
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from DataInterfaceHelper import dataInterfaceHelper
import pageNames
from ExtFinanceInterface import ExtFinanceInterface

dash.register_page(__name__, title="Value Investing",order=pageNames.pn['Value_investing'])
dih = dataInterfaceHelper()
gh = GraphHelper()
vih = ValueInvestingHelper()

def buildCompRow( df, ticker, marketE,table, graphType='line'):
    news=dih.getRssNews(ticker)
    compName=dih.get_company_name(ticker, marketE)
    fig=gh.getGraph(df,compName,ticker, marketE,"£", graphType)
    #fig=gh.buildFullGraph(compName,df)
    gr=dcc.Graph(figure=fig)
    row=dbc.Row([dbc.Col([gr],width={'size': 6}),
                    dbc.Col([table],width={'size': 3},style={"maxHeight": "900px"}),
                    dbc.Col(news,width={'size': 3},style={"maxHeight": "400px", "overflow": "scroll"}),
    ],style={"border":"2px black solid"})
    return html.Div(row)
    # set the sizing of the parent div
    #style = {'display': 'inline-block', 'width': '80%'})

layout = html.Div(
    [
        html.H1('Value Investing', style={'textAlign': 'center'}),
        
            dbc.Row([
            dbc.Col(
                [
                    dcc.Interval(
                        id="value_load_interval",
                        n_intervals=0,
                        max_intervals=0,  # <-- only run once
                        interval=1
                    ),
                    dbc.Spinner(html.Div(id="value_table"),spinner_style={"width": "3rem", "height": "3rem"}),
                #    html.Div(id='value_table'),
                #             #html.Div(id='markets_status')
                ], width=6
            ),

        ]),
        dbc.Row(
                [
                    dbc.Col(width={'size': 1}),
                    dbc.Col([
                       dcc.Dropdown(id='markets', placeholder='market...',
                            options=[{'label': 'FTSE 100', 'value': 'ftse100'},
                                {'label': 'FTSE 250', 'value': 'ftse250'},
                                {'label': 'DOW', 'value': 'dow'},
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
                                    'value': 'nasdaq_utilities'}]
                                ),
                        html.Br(),
                        dbc.Button("Review", id="review-btn", className="me-2", n_clicks=0),
                        dbc.Button("Update", id="update-btn", className="me-2", n_clicks=0),
                        html.Br(),
                        html.Br(),
                        ],width={'size': 3}),
                    dbc.Col([

                        ],
                        width={'size': 1})
                ],
        ),        
        dbc.Row([
            dbc.Col(
                [
                     dbc.Spinner(html.Div(id="val-inv-output"),spinner_style={"width": "3rem", "height": "3rem"}),                   
                ], width=6
            ),

         ]),
        # dbc.Row(
        #     [
                    dbc.Spinner(html.Div(id="val-inv-anal"),spinner_style={"width": "3rem", "height": "3rem"}),
                    #html.Div(id='candlestick_anal'),width={'size': 8}
                    #width={'size': 10})
            # ])

    ])

    
@callback(
    Output(component_id='val-inv-anal', component_property='children'),
    Input(component_id='markets', component_property='value'),
    Input(component_id="review-btn", component_property='n_clicks'),
)
def view_m(marketVal,revBton):
    efi=ExtFinanceInterface()
    if (marketVal == None):
        raise PreventUpdate
    marketE=markets_enum[marketVal]
    if "review-btn" == ctx.triggered_id:
        vih.processDataForMarket(marketE)
        tickers = vih.finalResults()
        #if not children:
        children=[]
        for tickerName in tickers:
            
            ticker = vih.getTicker(tickerName, marketE)
            try:
                data=dih.get_historical_data(ticker, datetime.now() + timedelta(days=-364), False)
                tData,dd=efi.getTickerDataTest(ticker, marketE)
                tb=gh.buildTable(tData)
                compRowData=buildCompRow(data,ticker, marketE, tb)
                children.append(compRowData)     
            except Exception as e:
                logging.getLogger().error(str(e))
                print(str(e))
        return children      
           
            
@callback(
    Output(component_id='value_table', component_property='children'),
    State(component_id='markets', component_property='value'),
    Input(component_id="update-btn", component_property='n_clicks'),
    Input(component_id="value_load_interval", component_property="n_intervals")
)
def build_market_data(marketVal, updateBtn, interv):
    if "update-btn" == ctx.triggered_id:
        marketE=markets_enum[marketVal.lower()]
        vih.financialInfo(marketE)   
        tData=vih.getTableStatusData()
        return dbc.Table.from_dataframe(tData,striped=True, bordered=True, hover=True,
                                        size='sm')," completed updatiing"
    else:
        tData=vih.getTableStatusData()
        return dbc.Table.from_dataframe(tData,striped=True, bordered=True, hover=True,
                                            size='sm')," completed updatiing"

        
            

        
        