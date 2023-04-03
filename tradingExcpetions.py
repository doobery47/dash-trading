class StockOutofDateException(Exception):
    "Raised when need to rerun Stock Update"
    pass

class ValueInvestmentOutofDateException(Exception):
    "Value invesmtnets data is either empty or out of date"
    pass

class InvalidDataException(Exception):
    "Invalid data from request or table construction"
    pass