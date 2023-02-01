import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, html, dcc, Output, Input, callback, State, MATCH
from dash import dash_table
import logging
from datetime import date
from dateutil.relativedelta import relativedelta
import datetime
import numpy as np


class GraphHelper:
    
    #https://www.marketwatch.com/investing/index/ukx/downloaddatapartial?startdate=08/03/2022 00:00:00&enddate=09/02/2022 23:59:59&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false&countrycode=uk
    
    def getGraph(self, df, marketName, currency,  graphType='line'):
        # get the last date in the db table. Update the table
        # create the graph and return
        
        df['MA50'] = df['close'].rolling(window=50, min_periods=0).mean()
        # df['MA200'] = df['close'].rolling(window=200, min_periods=0).mean()
        # df['MA200'].head(30)
        fig = go.Figure()
        lineColour='blue'
        
        # if(currentValue < startValue):
        #     lineColour="RebeccaPurple"
        
        # if(startValue !=0.0):
        #     fig = go.Figure(go.Indicator(
        #         align = 'center', mode = 'number+delta', value = currentValue,
        #         title = {
        #         'text': "Current value<br><span style='fontSize:0.8em;color:gray'>",
        #         'font':{'size':20}},
        #         delta = {
        #             'reference': startValue, 'relative': True, 'valueformat':'.2%',
        #             'font':{
        #             'size':18}},
        #             number = {
        #             'font':{
        #             'size':40}}))  
        
        if(graphType == 'line'):
            fig.add_trace(go.Scatter(x=df.index, y=df["open"]))
            #fig.add_trace(go.Scatter(data_frame=df,x=df.index, y=df["open"]))
            #fig = px.line(data_frame=df,x=df.index, y=df["open"])
            
        else:            
            fig.add_trace(go.Candlestick(x=df.index, open=df["open"], high=df["high"],
                        low=df["low"], close=df["close"], name="OHLC" ))

            fig.update_layout(xaxis_rangeslider_visible=False)
            
        fig.update_layout( 
            font=dict(
            family="Courier New, monospace",
            size=16,
            color=lineColour  
            ) ,         
            title=marketName+' historical price chart',
            yaxis_title='Stock Price (pence per Shares)',
            autosize=False,
            xaxis_tickangle=45,
            margin=dict(l=5, r=5, b=5, t=40, pad=5),
        )
        return fig
    
    def buildDashTable(self, dff, height=500):
        return dash_table.DataTable(
        id={
        'type': 'dynamic-table',
        'index': 0
        },
        style_as_list_view=True,
        style_cell={
        'height': 'auto',
        # all three widths are needed
        'minWidth': '200px', 'width': '200px', 'maxWidth': '200px',
        'whiteSpace': 'normal',
        'padding': '5px','textAlign': 'left'
    },
        #style_cell={'padding': '5px','textAlign': 'left'},   # style_cell refers to the whole table
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold',
            'border': '1px solid black'
        },
        style_data_conditional=[        # style_data.c refers only to data rows
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            },
             {'if': {'column_id': 'Description'},
            'width': '50%'},
            {'if': {'column_id': 'Name'},
            'width': '25%'},
                  
        ],
        fixed_rows={'headers': True},
        style_table={'height': '100%'},  # defaults to 500
        data=dff.to_dict('records'),
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        #columns=[{'id': x, 'name': x, 'presentation': 'markdown',"deletable": False, "selectable": False} if x == 'website' else {'id': x, 'name': x,"deletable": False, "selectable": False} for x in dff.columns],
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": False} for i in dff.columns
        ],
        editable=False,
        # filter_action="native",
        # sort_action="native",
        # sort_mode="multi",
        # row_selectable="multi",
        # row_deletable=False,
        # selected_rows=[],
        # page_action="native",
        # page_current=0,
        #page_size=10,
    ),
        css = list(
      list(
        selector = '.dash-cell div.dash-cell-value',
        rule = 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
      )
    ),
        
    def movingaverage(self, interval, window_size=10):
        window = np.ones(int(window_size))/float(window_size)
        return np.convolve(interval, window, 'same')
    
    def bbands(self, price, window_size=10, num_of_std=5):
        rolling_mean = price.rolling(window=window_size).mean()
        rolling_std = price.rolling(window=window_size).std()
        upper_band = rolling_mean + (rolling_std*num_of_std)
        lower_band = rolling_mean - (rolling_std*num_of_std)
        return rolling_mean, upper_band, lower_band

    def buildTable(self, dff, height=500):
    
        return html.Div(self.buildDashTable(dff, height=500)
        )
        
    def buildFullGraph(self, marketName,df):

        INCREASING_COLOR = '#17BECF'
        DECREASING_COLOR = '#7F7F7F'

        data = [dict(
            type='candlestick',
            open=df.open,
            high=df.high,
            low=df.low,
            close=df.close,
            x=df.index,
            yaxis='y2',
            name='GS',
            increasing=dict(line=dict(color=INCREASING_COLOR)),
            decreasing=dict(line=dict(color=DECREASING_COLOR)),
        )]

        layout = dict()

        fig = dict(data=data, layout=layout)
        fig['layout'] = dict()
        fig['layout']['plot_bgcolor'] = 'rgb(250, 250, 250)'
        fig['layout']['xaxis'] = dict(rangeselector=dict(visible=True))
        fig['layout']['yaxis'] = dict(
            domain=[0, 0.2], showticklabels=False)
        fig['layout']['yaxis2'] = dict(domain=[0.2, 0.8])
        fig['layout']['legend'] = dict(
            orientation='h', y=0.9, x=0.3, yanchor='bottom')
        fig['layout']['margin'] = dict(t=40, b=40, r=40, l=40)
        fig['layout']['title']=marketName

        # Add range buttons
        rangeselector = dict(
            visible=True,
            x=0, y=0.9,
            bgcolor='rgba(150, 200, 250, 0.4)',
            font=dict(size=13),
            buttons=list([
                dict(count=1,
                    label='reset',
                    step='all'),
                dict(count=1,
                    label='1yr',
                    step='year',
                    stepmode='backward'),
                dict(count=3,
                    label='3 mo',
                    step='month',
                    stepmode='backward'),
                dict(count=1,
                    label='1 mo',
                    step='month',
                    stepmode='backward'),
                dict(step='all')
            ]))

        fig['layout']['xaxis']['rangeselector'] = rangeselector
        mv_y = self.movingaverage(df.close)
        mv_x = list(df.index)

        # Clip the ends
        mv_x = mv_x[5:-5]
        mv_y = mv_y[5:-5]

        fig['data'].append(dict(x=mv_x, y=mv_y, type='scatter', mode='lines',
                                line=dict(width=1),
                                marker=dict(color='#E377C2'),
                                yaxis='y2', name='Moving Average'))

        # Set volume bar chart colors
        colors = []

        for i in range(len(df.close)):
            if i != 0:
                if df.close[i] > df.close[i-1]:
                    colors.append(INCREASING_COLOR)
                else:
                    colors.append(DECREASING_COLOR)
            else:
                colors.append(DECREASING_COLOR)

        # Add volume bar chart

        fig['data'].append(dict(x=df.index, y=df.volume,
                                marker=dict(color=colors),
                                type='bar', yaxis='y', name='volume'))

        bb_avg, bb_upper, bb_lower = self.bbands(df.close)
        
        fig['data'].append(dict(x=df.index, y=bb_upper, type='scatter', yaxis='y2',
                        line=dict(width=1),
                        marker=dict(color='#ccc'), hoverinfo='none',
                        legendgroup='Bollinger Bands', name='Bollinger Bands'))

        fig['data'].append(dict(x=df.index, y=bb_lower, type='scatter', yaxis='y2',
                                line=dict(width=1),
                                marker=dict(color='#ccc'), hoverinfo='none',
                                legendgroup='Bollinger Bands', showlegend=False))

        return fig