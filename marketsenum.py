
from enum import Enum


class markets_enum(Enum):
    #__order__ = 'ftse100 ftse250 dow nasdaq s_and_p'
    ftse100=1
    ftse250=2
    #ftse350=3
    #ftseAllShares=5
    dow=6
    s_and_p=8,
    nasdaq=9
    nasdaq_BasicMaterials=10,
    nasdaq_ConsumerDiscretionary=11,
    nasdaq_ConsumerStaples=12,
    nasdaq_Energy=13,
    nasdaq_Finance=14,
    nasdaq_HealthCare=15,
    nasdaq_Industrials=16,
    nasdaq_Miscellaneous=17,
    nasdaq_RealEstate=18,
    nasdaq_Technology=19,
    nasdaq_Telecommunications=20,
    nasdaq_Utilities=21,
    none=22
  
    
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
    
    