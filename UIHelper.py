
from DataBaseHelper import DataBaseHelper
from dash import  dcc

## This class is to contain functions to build re-usable ui elemenets
class UIHelper(DataBaseHelper):
    def __init__(self):
        DataBaseHelper.__init__(self)
        
    def companyNameDropDown(self, marketE, dropdownName):
        options=[]
        tickers = tickers = self.get_stocks_list(marketE)
        for ticker in tickers:
            compName=self.get_company_name(ticker,marketE)
            options.append({'label': compName, 'value': ticker.tickerStrpName})
        
        dd=dcc.Dropdown(
            id={
                'type': dropdownName,
                'index': 0,
            }, placeholder='Company',
            options=options)
        return dd
