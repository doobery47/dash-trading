
from enum import Enum


class markets_enum(Enum):
    #__order__ = 'ftse100 ftse250 dow nasdaq s_and_p'
    ftse100=1
    ftse250=2
    #ftse350=3
    #ftseAllShares=5
    dow=6
    s_and_p=8
    nasdaq=9
    nasdaq_basic_materials=10
    nasdaq_consumer_discretionary=11
    nasdaq_consumer_staples=12
    nasdaq_energy=13
    nasdaq_finance=14
    nasdaq_health_care=15
    nasdaq_industrials=16
    nasdaq_miscellaneous=17
    nasdaq_realestate=18
    nasdaq_technology=19
    nasdaq_telecommunications=20
    nasdaq_utilities=21
  
    
    def tableName(self):
        return self.name+"HistoricValues"
    
class markets_enum_helper: 
    #marketsE = markets_enum.none
     
    def __init__(self, marketsE):
        self._marketsE = marketsE
        
    @property
    def tableName(self):
        return self._marketsE.name+"HistoricValues"
    @property
    def marketName(self):
        return self._marketsE.name
    

    