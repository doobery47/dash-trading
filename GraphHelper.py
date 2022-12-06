import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, html, dcc, Output, Input, callback, State, MATCH
from dash import dash_table


class GraphHelper:
    
    #https://www.marketwatch.com/investing/index/ukx/downloaddatapartial?startdate=08/03/2022 00:00:00&enddate=09/02/2022 23:59:59&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false&countrycode=uk
    
    def getGraph(self, df, marketName, currency, currentValue=0.0, startValue=0.0, graphType='line'):
        # get the last date in the db table. Update the table
        # create the graph and return
        
        df['MA50'] = df['close'].rolling(window=50, min_periods=0).mean()
        df['MA200'] = df['close'].rolling(window=200, min_periods=0).mean()
        df['MA200'].head(30)
        fig = go.Figure()
        
        if(startValue !=0.0):
            fig = go.Figure(go.Indicator(
                align = 'center', mode = 'number+delta', value = currentValue,
                title = {
                'text': "Current value<br><span style='fontSize:0.8em;color:gray'>",
                'font':{'size':20}},
                delta = {
                    'reference': startValue, 'relative': True, 'valueformat':'.2%',
                    'font':{
                    'size':18}},
                    number = {
                    'font':{
                    'size':40}}))  
        
        if(graphType == 'line'):
            fig.add_trace(go.Scatter(x=df.index, y=df["open"]))
            #fig.add_trace(go.Scatter(data_frame=df,x=df.index, y=df["open"]))
            #fig = px.line(data_frame=df,x=df.index, y=df["open"])
            
        else:            
            print(df)
            fig.add_trace(go.Candlestick(x=df.index, open=df["open"], high=df["high"],
                        low=df["low"], close=df["close"], name="OHLC" ))

            #fig = go.Figure(data=[candlestick])

            fig.update_layout(xaxis_rangeslider_visible=False)
            
        fig.update_layout( 
            font=dict(
            family="Courier New, monospace",
            size=16,
            color="RebeccaPurple"  
            ) ,         
            title=marketName+' historical price chart',
            yaxis_title='Stock Price (pence per Shares)',
            autosize=False,
            xaxis_tickangle=45,
            margin=dict(l=5, r=5, b=5, t=40, pad=5),
        )
        return fig
    
    headerColours = {"currentIsaColour":'#C750BB', "historicIsaColour":"#50BBC7",
                      "currentPIPColour":"#C750BB","historicPIPColour":"#7a49a5"}
    
#     def createPlotlyList(self, headers, columns, headerColour):
#         rowEvenColor = 'lightgrey'
#         rowOddColor = 'white'
#         fig = go.Figure(data=[go.Table(columnwidth=[5,1,1],
#         header=dict(values=headers, fill_color=headerColour, align='left' ),
#         cells=dict(values=columns,
#                 align=['left', 'center'], 
#                 font_size=12,
#                 fill_color = [[rowOddColor,rowEvenColor]*40],
#                 line_color='darkslategray', 
#                 ))])
#         fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        
#         return fig
        
# # gh = GraphHelper()
# # gh.getGraph(markets_enum.ftse100)

    def buildTable(self, dff, height=500):
    
        return html.Div(
                    dash_table.DataTable(
                        id={
                        'type': 'dynamic-table',
                        'index': 0
                    },
                        style_as_list_view=True,
                        style_cell={'padding': '5px'},   # style_cell refers to the whole table
                        style_header={
                            'backgroundColor': 'white',
                            'fontWeight': 'bold',
                            'border': '1px solid black'
                        },
                    #----------------------------------------------------------------
                    # Striped Rows
                    #----------------------------------------------------------------
                        # style_header={
                        #     'backgroundColor': 'rgb(230, 230, 230)',
                        #     'fontWeight': 'bold'
                        # },
                        style_data_conditional=[        # style_data.c refers only to data rows
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                            },
                            {'if': {'column_id': 'Name'},
                            'width': '50%'}
                        ],
                        fixed_rows={'headers': True},
                        style_table={'height': height},  # defaults to 500
                        data=dff.to_dict('records'),
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                        },
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
                        # page_action="native",
                        # page_current=0,
                        #page_size=10,
                    )
        )
    
    