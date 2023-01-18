import dash
from dash import Dash, dcc, html,callback, ctx
from dash.dependencies import Input, Output
from dash import Input, MATCH, Output, callback, dcc, html
import dash_bootstrap_components as dbc
import pageNames

logFileName='dash-trading.log'

dash.register_page(__name__, order=pageNames.pn['logview'])

btn_style={'backgroundColor': '#111100', 
           'color':'white','width':'100%' , 'border':'1.5px black solid','height': '50px','text-align':'center', 'marginLeft': '20px', 'marginTop': '20px'}

layout = html.Div([
    dbc.Row(
            [
                dbc.Col(width={'size': 1}),
                dbc.Col([
                    dcc.Interval(
                        id="load_interval",
                        n_intervals=0,
                        max_intervals=0,  # <-- only run once
                        interval=1
                    ),
                    dcc.Textarea(
                        id='logfile-output',
                        value='Textarea content initialized\nwith multiple lines of text',
                        style={'width': '100%', 'height': 800},
                    ),
                    html.Br(),
                    dbc.Button("Clear", id="clr-btn", className="me-2", n_clicks=0),
                    dbc.Button("Refresh", id="refresh-btn", className="me-2", n_clicks=0)
                    ],width={'size': 9}),
                dbc.Col([
                    # dbc.Button("Top", id="top-btn", className="me-2", n_clicks=0),
                    # dbc.Button("Bottom", id="bottom-btn", className="me-2", n_clicks=0)
                    ],
                    width={'size': 1})
            ],
    ),
    
 
])

@callback(
    Output('logfile-output', 'value'),
    Input(component_id="load_interval", component_property="n_intervals"),
    Input(component_id="clr-btn", component_property='n_clicks'),
    Input(component_id="refresh-btn", component_property='n_clicks'),
)
def update_output(n_intervals: int, clearbtn, refresh):
    if "clr-btn" == ctx.triggered_id:
        open(logFileName, "w").close()
        
    f=open(logFileName, 'r')
    LogOutput=f.read()
    f.close()
    return LogOutput



# with open('datatableTest.py') as this_file:
#     for a in this_file.read():
#         if "\n" in a:
#             text_markdown += "\n \t"
#         else:
#             text_markdown += a