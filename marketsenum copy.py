
from enum import Enum


class markets_enum(Enum):
    #__order__ = 'ftse100 ftse250 dow nasdaq s_and_p'
    ftse100=1
    ftse250=2
    #ftse350=3
    #ftseAllShares=5
    dow=6
    nasdaq=7
    s_and_p=8
    none=9
    
    def tableName(self):
        return self.name+"HistoricValues"
    
class markets_enum_helper: 
    marketsE = markets_enum.none
     
    def __init__(self, marketsE):
        self._marketsE = marketsE
        
    @property
    def tableName(self):
        return self._marketsE.name+"HistoricValues"
    @property
    def marketName(self):
        return self._marketsE.name
    
    