
from BaseHelper import BaseHelper
from dash import  dcc

## This class is to contain functions to build re-usable ui elemenets
class UIHelper(BaseHelper):
    def __init__(self):
        BaseHelper.__init__(self)
        
    def companyNameDropDown(self, marketE, dropdownName):
        options=[]
        tickers = tickers = self.getTickersList(marketE)
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
