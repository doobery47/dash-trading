import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, title="Value Investing",order=6)

def layout():
    return dbc.Row([
        dbc.Col([
    dcc.Markdown('# Value Investing', className='mt-3'),
        ], width={'size':6, 'offset':2})
], justify='center')