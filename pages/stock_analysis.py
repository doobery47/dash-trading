import dash
import dash_bootstrap_components as dbc
from marketsenum import markets_enum
from dash import ALL, Input, Output, State, callback, dcc, html

from marketsenum import markets_enum
from StockAnalysisHelper import StockAnalysisHelper
import pageNames
from dash.exceptions import PreventUpdate
from GraphHelper import GraphHelper
from datetime import datetime
from dateutil.relativedelta import relativedelta
from DataInterfaceHelper import dataInterfaceHelper
from Calculations import TradingCalculations
from ValueInvestingHelper import ValueInvestingHelper


dash.register_page(
    __name__, title="Stock Analysis", order=pageNames.pn["stock_analysis"]
)

sah = StockAnalysisHelper()

df = None


layout = html.Div(
    [
        html.H1("Stock Analysis", style={"textAlign": "center"}),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            dcc.Dropdown(
                                id="namrket-names",
                                placeholder="Update market...",
                                options=[
                                    {"label": "FTSE 100", "value": "ftse100"},
                                    {"label": "FTSE 250", "value": "ftse250"},
                                    {"label": "DOW", "value": "dow"},
                                    {
                                        "label": "NASDAQ-Basic Materials",
                                        "value": "nasdaq_basic_materials",
                                    },
                                    {
                                        "label": "NASDAQ-Consumer Discretionary",
                                        "value": "nasdaq_consumer_discretionary",
                                    },
                                    {
                                        "label": "NASDAQ-Consumer Staples",
                                        "value": "nasdaq_consumer_staples",
                                    },
                                    {
                                        "label": "NASDAQ-Energy",
                                        "value": "nasdaq_energy",
                                    },
                                    {
                                        "label": "NASDAQ-Finance",
                                        "value": "nasdaq_finance",
                                    },
                                    {
                                        "label": "NASDAQ-Health Care",
                                        "value": "nasdaq_health_care",
                                    },
                                    {
                                        "label": "NASDAQ-Industrials",
                                        "value": "nasdaq_industrials",
                                    },
                                    {
                                        "label": "NASDAQ-Miscellaneous",
                                        "value": "nasdaq_miscellaneous",
                                    },
                                    {
                                        "label": "NASDAQ-Real Estate",
                                        "value": "nasdaq_realestate",
                                    },
                                    {
                                        "label": "NASDAQ-Technology",
                                        "value": "nasdaq_technology",
                                    },
                                    {
                                        "label": "NASDAQ-Telecommunications",
                                        "value": "nasdaq_telecommunications",
                                    },
                                    {
                                        "label": "NASDAQ-Utilities",
                                        "value": "nasdaq_utilities",
                                    },
                                ],
                            ),
                            style={"marginBottom": 50, "marginTop": 50, "width": "40%"},
                        ),
                    ],
                    width={"size": 6},
                ),
                dbc.Col(
                    [
                        html.H4("Analysis period", style={"textAlign": "left"}),
                        html.Div(
                            [
                                dcc.RadioItems(
                                    id="analyis-period",
                                    options=[
                                        dict(label="1 years", value="oneYear"),
                                        dict(label="2 years", value="twoYears"),
                                        dict(label="3 years", value="threeYears"),
                                    ],
                                    labelStyle={"display": "block"},
                                    style={
                                        "fontSize": 20,
                                        "marginLeft": "15px",
                                        "marginBottom": "20px",
                                    },
                                    inputStyle={"marginRight": "20px"},
                                    value="threeYears",
                                )
                            ]
                        ),
                    ],
                    width={"size": 3},
                ),
                dbc.Col(
                    [
                        html.H4("Apply value investing", style={"textAlign": "left"}),
                        html.Div(
                            [
                                dcc.RadioItems(
                                    id="value-investing",
                                    options=[
                                        dict(label="yes", value="yes"),
                                        dict(label="no", value="no"),
                                    ],
                                    labelStyle={"display": "block"},
                                    style={
                                        "fontSize": 20,
                                        "marginLeft": "15px",
                                        "marginBottom": "20px",
                                    },
                                    inputStyle={"marginRight": "20px"},
                                    value="no",
                                )
                            ]
                        ),
                    ],
                    width={"size": 3},
                ),
                dbc.Spinner(
                    html.Div(id="anal-table"),
                    spinner_style={"width": "3rem", "height": "3rem"},
                ),
            ]
        ),
        dbc.Row([dbc.Col([html.Div(id="comp-analysis-gr")], width={"size": 12})]),
        dbc.Row([dbc.Col([html.Div(id="comp-analysis-news")], width={"size": 12})]),
    ]
)


@callback(
    Output(component_id="anal-table", component_property="children"),
    Input(component_id="namrket-names", component_property="value"),
    Input(component_id="analyis-period", component_property="value"),
    Input(component_id="value-investing", component_property="value"),
)
def build_market_data(marketVal, analPeriod, valueInvesting):
    if marketVal != None:
        marketE = markets_enum[marketVal]
        performaceStock, dates = sah.topShares(marketE, analPeriod)
        if valueInvesting == "yes":
            vih = ValueInvestingHelper()
            tickerNames = performaceStock["ticker"].tolist()
            tickers2Proc = []
            for tickerName in tickerNames:
                tickers2Proc.append(vih.getTicker(tickerName, marketE))

            vih.processDataForTickers(tickers2Proc, marketE)
            vih_tickers = vih.finalResults()
            print(performaceStock)
            print(vih_tickers)
            performaceStock = performaceStock[
                performaceStock["ticker"].isin(vih_tickers)
            ]
        df = performaceStock
        df["id"] = df["ticker"]
        df.set_index("id", inplace=True, drop=False)
        # create an interactive table from list
        if performaceStock.shape[0] > 0:
            return sah.buildDashTable(performaceStock, dates, marketE)
    else:
        raise PreventUpdate


@callback(
    Output(component_id="comp-analysis-gr", component_property="children"),
    Output(component_id="comp-analysis-news", component_property="children"),
    Input(component_id={"type": "dyn-analysis-table", "index": ALL}, component_property="active_cell"),
    State(component_id={"type": "dyn-analysis-table", "index": ALL}, component_property="data"),
    State(component_id="namrket-names", component_property="value"),
)
def buildGraph(actCell, data, marketStr):
    if not actCell or actCell[0] == None:
        raise PreventUpdate
    dih = dataInterfaceHelper()
    tc = TradingCalculations()
    gh = GraphHelper()

    marketE = markets_enum[marketStr]
    # if(actCell.column ==6): # Yahoo url

    tickerStr = data[0][actCell[0]["row"]]["ticker"]

    ticker = sah.getTicker(tickerStr, marketE)
    compName = sah.get_company_name(ticker, marketE)
    data = dih.get_historical_data(
        ticker, str((datetime.now() - relativedelta(years=3)).date())
    )
    children = []

    gr = gh.getGraph(
        data, compName, ticker, marketE, "£", "line", simpleLinearRegresion=True
    )
    gr.update_layout(margin=dict(t=100, b=5, l=2, r=2),width=1500, height=700)
    children.append(
        dcc.Graph(
            id={"type": "dynamic-graph", "index": 0},
            figure=gr,
        )
    )
    news = dih.getRssNews(ticker.tickerYahoo, "16px")
    return children, news
