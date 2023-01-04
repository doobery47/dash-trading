from DataBaseHelper import DataBaseHelper
import pandas as pd
from  PortfolioTypeE import PortfolioTypeE
from operator import itemgetter
from yahoo_fin import stock_info as si
import logging

class PortfolioHelper(DataBaseHelper):
    
    def __init__(self):
        DataBaseHelper.__init__(self)

    def calcProfitLoss(self):
        print(self)
        
    def isSold(self):
        print(self)
               
    #go through the tale and group list into individual shares
    def getInvestments(self,pte, oldInvestments=True, owner="Colin"):
        df=None
        tickerVals={}
        
        if(pte == PortfolioTypeE.ManagedFundsISA):
            df = pd.read_sql_query("SELECT * from isa_investments where owner='"+owner+"'", DataBaseHelper.conn)
        elif(pte == PortfolioTypeE.SIP):
            df = pd.read_sql_query("SELECT * from pip_investments where owner='"+owner+"'", DataBaseHelper.conn)
        
        df=df.drop(df[df.name_a == ""].index)
        print(df['name_a'])
        currentName=""
        currentTicker=[]
        for rowIndex, row in df.iterrows():           
            if(row['name_a']==None):
                continue
            if(row['name_b']!=None):
                name=(row['name_a']+":"+row['name_b']).lstrip()
            else:
                name=row['name_a'].lstrip()
                
            if(name in tickerVals):
                currentTicker=tickerVals[name]
            else:
                currentTicker=[]
                                          
            currentName=name
            currentTicker.append(row)
            tickerVals[currentName]=currentTicker
       
        return tickerVals            

    # determine if there any shares outstanding
    # Calculate the profit or loss
    def calcTicker(self, name, tickerData):
        profit=0
        quantityOutstanding=0
            
        for tickerRec in tickerData:
            profit=profit+float(tickerRec['totalcost'])
            if(tickerRec['status']=='Sold'):
                quantityOutstanding=quantityOutstanding+int(tickerRec['quantity'])
            elif(tickerRec['status']=='Bought'):
                quantityOutstanding=quantityOutstanding-tickerRec['quantity']
        
        return {'Name': name, 'Outstanding': quantityOutstanding, 'Profit_Loss': round(profit*-1,2), "Close_Date": tickerRec['date'], "Last_Purchase":tickerData[0]['date'] }
       
    def getHistoricInvestments(self,pte, owner="Colin"):
        tickerDict=self.getInvestments(pte,True, owner)
        dfSold = pd.DataFrame(columns=['Name','Profit_Loss', 'Close_Date'])
 
        soldCount=0
        profitLossVal=0.0
        
        for key in tickerDict:
            print(key)
            tickerRec=self.calcTicker(key, tickerDict.get(key))
            outstanding=None
            # As a margin of error we have assumed anything less than 2 outstanding is historic and and anything
            # greater than 2 outstanding for a investment is current
            if(abs(tickerRec['Outstanding']) <2):
                dfSold.loc[soldCount] = [tickerRec['Name'], tickerRec['Profit_Loss'], tickerRec['Close_Date']]
                soldCount = soldCount+1
                profitLossVal=profitLossVal+float(tickerRec['Profit_Loss'])
                
        dfSold.loc[soldCount]=["Total", round(profitLossVal,2), ""]
        return dfSold
    
    def getCurrentInvestments(self,pte, owner):
        tickerDict=self.getInvestments(pte,False, owner)
        dfCurrent = pd.DataFrame(columns=['Name','Profit_Loss', 'Outstanding','Last_Purchase'])

        currentCount=0
        profitLossVal=0.0
        
        for key in tickerDict:
            print(key)
            tickerRec=self.calcTicker(key, tickerDict.get(key))
            outstanding=None
            if(abs(tickerRec['Outstanding']) >=2):
                # --profit loss calculation
                # shares held * current price - cost of purchase of shares
                dfCurrent.loc[currentCount] = [tickerRec['Name'], tickerRec['Profit_Loss'], abs(tickerRec['Outstanding']), tickerRec['Last_Purchase']]
                
                tick=tickerDict.get(key)[0]['ticker']
                if(tick==None):
                    profitLossVal=0
                else:
                    currentVal=si.get_live_price(tick)
                    profitLossVal=(tickerRec['Outstanding']*currentVal)-profitLossVal
                currentCount=currentCount+1
                #profitLossVal=profitLossVal+float(tickerRec['Profit_Loss'])
                
                
        dfCurrent.loc[currentCount]=["Total", round(profitLossVal,2), "",""]
                
        return dfCurrent
        
# ph=PortfolioHelper()
# ph.getHistoricInvestments(True)