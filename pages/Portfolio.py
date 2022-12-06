from marketsenum import markets_enum
from CandelstickAnalHelper import CandlestickAnalHelper
from PortfolioHelper import PortfolioHelper
from GraphHelper import GraphHelper
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, html, dcc, Output, Input, callback
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from PortfolioTypeE import PortfolioTypeE
import GraphHelper as gh
from dash import dash_table

dash.register_page(__name__,  order=2)

ph = PortfolioHelper()
gHelper = gh.GraphHelper()
breakout_perc = 2
breakout_trading_range = 16
breakout = "None"
ca = CandlestickAnalHelper()
#dff = ph.getHistoricInvestments(PortfolioTypeE.ManagedFundsISA, 'Colin')
# dff = pd.DataFrame({“Symbol”:['alpha','beta',‘gamma’],“Currency”:['USD','USD','USD'],“Price unit”:['1','1','1'],
# “Trade Unit”:[‘Kg’,‘Kg’,‘Kg’], “Lot Size”:['15','1','1'],“Tick Size”:['1','.01','.01']})

def tableCreation(dff):
               return html.Div([
                dash_table.DataTable(
                    id='datatable_id',
                    data=dff.to_dict('records'),
                    columns=[
                        {"name": i, "id": i, "deletable": False, "selectable": False} for i in dff.columns
                    ],
                    editable=False,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    row_selectable="multi",
                    row_deletable=False,
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                    # page_action='none',
                    # style_cell={
                    # 'whiteSpace': 'normal'
                    # },
                    # fixed_rows={ 'headers': True, 'data': 0 },
                    # virtualization=False,
                    # style_cell_conditional=[
                    #     {'if': {'column_id': 'countriesAndTerritories'},
                    #     'width': '40%', 'textAlign': 'left'},
                    #     {'if': {'column_id': 'deaths'},
                    #     'width': '30%', 'textAlign': 'left'},
                    #     {'if': {'column_id': 'cases'},
                    #     'width': '30%', 'textAlign': 'left'},
                ),
            ])

chart_styles = [
    'default', 'binance', 'blueskies', 'brasil',
    'charles', 'checkers', 'classic', 'yahoo',
    'mike', 'nightclouds', 'sas', 'starsandstripes'
]

layout = html.Div(
    [
        html.H1('Portfolio', style={'textAlign': 'center'}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4('Investment type', style={
                                'textAlign': 'left'}),
                        html.Div([dcc.RadioItems(id='inv-type',
                            options=[dict(label='PIP', value=PortfolioTypeE.PIP.name),
                                    dict(
                                        label='Managed Funds ISAs', value=PortfolioTypeE.ManagedFundsISA.name),
                                    dict(
                                        label='Equities - ISAs', value=PortfolioTypeE.EquitiesISA.name),
                                    dict(
                                        label='Managed Funds', value=PortfolioTypeE.ManagedFunds.name),
                                    dict(label='Equities', value=PortfolioTypeE.Equities.name)],
                            labelStyle={
                                'display': 'block'},
                            style={
                                'fontSize': 20, "marginLeft": "15px", "marginBottom": "20px"},
                            inputStyle={
                                "marginRight": "20px"},
                            value='Managed Funds ISAs')]),
                    ]#, xs=10, sm=10, md=8, lg=4, xl=4, xxl=4
                ),
                dbc.Col(
                    [
                        html.H4('Time zone', style={'textAlign': 'left'}),
                        html.Div([dcc.RadioItems(id='hist_status',
                                                 options=[dict(label='Current', value='Current'),
                                                          dict(
                                                              label='Historical', value='Historical'),
                                                          ],
                                                 labelStyle={
                                                     'display': 'block'},
                                                 style={
                                                     'fontSize': 20, "marginLeft": "15px", "marginBottom": "20px"},
                                                 inputStyle={
                                                     "marginRight": "20px"},
                                                 value='hist_status')])
                    ]#, xs=10, sm=10, md=8, lg=4, xl=4, xxl=4
                ),
                dbc.Col(
                    [
                        html.H4('Owner', style={'textAlign': 'left'}),
                        html.Div([dcc.RadioItems(id='owner',
                                                 options=[dict(label='None selected', value='None selected'),
                                                          dict(label='Colin',
                                                               value='Colin'),
                                                          dict(label='Sandra',
                                                               value='Sandra'),
                                                          ],
                                                 value='None selected',
                                                 labelStyle={
                                                     'display': 'block'},
                                                 style={
                                                     'fontSize': 20, "marginLeft": "15px", "marginBottom": "20px"},
                                                 inputStyle={
                                                     "marginRight": "20px"},
                                                 )])
                    ]#, xs=10, sm=10, md=8, lg=4, xl=4, xxl=4
                ),

            ]
        ),
        dbc.Row(
            [               
                html.Div(id='dataframe_output', style={'padding-right': '60px'}),
            ])

    ])


@callback(
    Output('dataframe_output', 'children'),
    Input(component_id='inv-type', component_property='value'),
    Input(component_id='hist_status', component_property='value'),
    Input(component_id='owner', component_property='value'),prevent_initial_call=True
)
def build_graphs(marketVal, histStatusVal, ownerVal):
    gh=GraphHelper()
    print(marketVal)
    print(histStatusVal)
    print(ownerVal)

    #global dff
    #dff = ph.getHistoricInvestments(PortfolioTypeE.ManagedFundsISA, 'Colin')

    if ownerVal != 'None selected':
        if marketVal == "ManagedFundsISA" and histStatusVal == 'Historical':
            dff = ph.getHistoricInvestments(PortfolioTypeE[marketVal], ownerVal)
            print(dff)
            #return tableCreation(dff)
        elif marketVal == "ManagedFundsISA" and histStatusVal == 'Current':
            dff = ph.getCurrentInvestments(PortfolioTypeE[marketVal], ownerVal)
            print(dff)
            #return tableCreation(dff)
        elif marketVal == "PIP" and histStatusVal == 'Historical':
            dff = ph.getHistoricInvestments(PortfolioTypeE[marketVal], ownerVal)
            #return tableCreation(dff)
        elif marketVal == "PIP" and histStatusVal == 'Current':
            dff = ph.getCurrentInvestments(PortfolioTypeE[marketVal], ownerVal)
            print(dff)
            #return tableCreation(dff)
        return gh.buildTable(dff,800)
        # else:
        #     return dff.to_dict('records')
        # elif pte==PortfolioTypeE.Equities and histStatusVal == 'Historical':
        #     #st.subheader("Historical equities investments - "+ownerVal)
        #     #dfInv=ph.getCurrentInvestments(pte, ownerVal)
        # elif pte==PortfolioTypeE.Equities and histStatusVal == 'Current':
        #     #st.subheader("Current equities investments - "+ownerVal)
        #     #dfInv=ph.getCurrentInvestments(pte, ownerVal)
    # else:
    #         return dff
