import dash
from dash import Dash, html, dcc, Output, Input, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

from GraphHelper import GraphHelper
import DataInterfaceHelper
from marketsenum import markets_enum
import logging
from DataInterfaceHelper import dataInterfaceHelper

#di = DataInterfaceHelper.dataInterfaceHelper()
dih = dataInterfaceHelper()
gh = GraphHelper()

dash.register_page(__name__, path="/", title="Home")

dih.UpdateMarketData(markets_enum.ftse100)
dih.UpdateMarketData(markets_enum.ftse250)
dih.UpdateMarketData(markets_enum.dow)
dih.UpdateMarketData(markets_enum.s_and_p)
dih.UpdateMarketData(markets_enum.nasdaq)



def buildCompRow(children,marketE, noYears, chosen_chart_type):
    df = dih.get_marketData(marketE, noYears)
    openVal, closeVal = dih.getMarketCurrentValue(marketE) 
    fig = gh.getGraph(df, marketE.name,None,marketE, "pence", chosen_chart_type)
    graph=dcc.Graph(figure=fig)
    footer=createFooter(openVal,closeVal)  
    
    marketTicker=dih.getMarketTicker(marketE)
    news=dih.getRssNews(marketTicker, '16px')
    row=dbc.Row([dbc.Col([graph,footer],width={'size': 5}),
                dbc.Col(news,width={'size': 5},style={"maxHeight": "400px", "overflow": "scroll"}),
    ],style={"border":"2px black solid"})
    children.append(html.Div(row))
    return children

def get_percentage_diff(previous, current):
    try:
        percentage = abs(previous - current)/max(previous, current) * 100
    except ZeroDivisionError:
        percentage = float('inf')
    return percentage
def createFooter(current, close):
    # NEED TO TAKE INTO CONSIDERATION THE DATE IE WEEKEND
    percChange = get_percentage_diff(close,current)
    if(current > close):
        return html.Div("Current= "+str(round(current,2))+" Previous Close="+str(round(close,2))+" Change="+str(round(percChange,2))+"%", 
                    className="bg-opacity-75 p-2 m-1 bg-primary text-light fw-bold rounded")
    elif(current < close):
        return html.Div("Current= "+str(round(current,2))+" Previous Close="+str(round(close,2))+" Change="+str(round(percChange,2))+"%", 
                    className="bg-opacity-75 p-2 m-1 bg-danger text-light fw-bold rounded")
    else:
        return html.Div("Current= "+str(round(current,2))+" Previous Close="+str(round(close,2))+" Change="+str(round(percChange,2))+"%", 
                    className="bg-opacity-75 p-2 m-1 bg-secondary text-light fw-bold rounded")

layout = html.Div(
    [
        html.H1("Market data", style={"textAlign": "center"}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4(
                            "Date range",
                            style={"textAlign": "left", "marginLeft": "20px"},
                        ),
                        html.Div(
                            [
                                
                                dcc.RadioItems(
                                    id="date-range",
                                    options=[
                                            {"label":"year to date", "value":1},
                                            {"label":"two years to date", "value":2},
                                            {"label":"three years to date", "value":3}
 
                                    ],
                                    labelStyle={"display": "block"},
                                    style={
                                        "fontSize": 20,
                                        "marginLeft": "15px",
                                        "marginBottom": "20px",
                                    },
                                    inputStyle={"marginRight": "20px"},
                                    value=1,
                                )
                            ]
                        ),
                    ],
                    xs=10,
                    sm=10,
                    md=8,
                    lg=4,
                    xl=4,
                    xxl=4,
                ),
                dbc.Col(
                    [
                        html.H4("Chart type", style={"textAlign": "left"}),
                        html.Div(
                            [
                                dcc.RadioItems(
                                    id="chart-type",
                                    options=[
                                        dict(label="Line", value="line"),
                                        dict(label="Candle", value="candle"),
                                    ],
                                    labelStyle={"display": "block"},
                                    style={
                                        "fontSize": 20,
                                        "marginLeft": "15px",
                                        "marginBottom": "20px",
                                    },
                                    inputStyle={"marginRight": "20px"},
                                    value="line",
                                )
                            ]
                        ),
                    ],
                    xs=10,
                    sm=10,
                    md=8,
                    lg=4,
                    xl=4,
                    xxl=4,
                ),
            ]
        ),
        html.Div(id='market-data')
 
    ]
)


@callback(
    Output(component_id="market-data", component_property="children"),
    Input(component_id="date-range", component_property="value"),
    Input(component_id="chart-type", component_property="value"),
)
# represents that which is assigned to the component property of the Input
def build_graphs(noYears, chosen_chart_type):
    
    children=[]
    
    children = buildCompRow(children,markets_enum.ftse100,noYears, chosen_chart_type)
    children = buildCompRow(children,markets_enum.ftse250,noYears, chosen_chart_type)
    children = buildCompRow(children,markets_enum.dow,noYears, chosen_chart_type)
    children = buildCompRow(children, markets_enum.s_and_p ,noYears, chosen_chart_type)
    children = buildCompRow(children,markets_enum.nasdaq, noYears, chosen_chart_type)
                   
    return children
  

# if __name__ == '__main__':
#     app.run_server(port=8051)
