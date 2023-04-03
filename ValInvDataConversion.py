


from BaseHelper import BaseHelper
import pandas as pd
from PortfolioTypeE import PortfolioTypeE
from operator import itemgetter
from yahoo_fin import stock_info as si
import logging
import ast
from datetime import date, datetime, timedelta
import logging
import sys
import dropables
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Date,
    Float,
    BigInteger,
)
from marketsenum import markets_enum


class ValInvDataConversion(BaseHelper):
    def __init__(self):
        BaseHelper.__init__(self)

    def createBalanceSheetTable(self):
        try:
            meta = MetaData()
            tab = Table(
                "val_inv_anal_balsheet",
                meta,
                Column("date", Date),
                Column("epic", String),
                Column("market", String),
                Column("intangibleAssets", BigInteger),
                Column("intangibleAssets", BigInteger),
                Column("capitalSurplus", BigInteger),
                Column("totalLiab", BigInteger),
                Column("investmentsinAssociatesatCost", BigInteger),
                Column("otherCurrentLiab", BigInteger),
                Column("totalAssets", BigInteger),
                Column("commonStock", BigInteger),
                Column("otherCurrentAssets", BigInteger),
                Column("retainedEarnings", BigInteger),
                Column("otherLiab", BigInteger),
                Column("treasuryStock", BigInteger),
                Column("otherAssets", BigInteger),
                Column("cash", BigInteger),
                Column("totalCurrentLiabilities", BigInteger),
                Column("deferredLongTermAssetCharges", BigInteger),
                Column("shortLongTermDebt", BigInteger),
                Column("otherStockholderEquity", BigInteger),
                Column("propertyPlantEquipment", BigInteger),
                Column("totalCurrentAssets", BigInteger),
                Column("longTermInvestments", BigInteger),
                Column("netTangibleAssets", BigInteger),
                Column("netReceivables", BigInteger),
                Column("minorityInterest", BigInteger),
                Column("goodWill", BigInteger),
                Column("inventory", BigInteger),
                Column("shortTermInvestments", BigInteger),
                Column("deferredLongTermLiab", BigInteger),
                Column("longTermDebt", BigInteger),
                Column("accountsPayable", BigInteger),
            )
            meta.create_all(self.engine)
        except Exception as e:
            print(e)

    def createCashStatementTable(self):
        try:
            meta = MetaData()
            tab = Table(
                "val_inv_anal_cashsheet",
                meta,
                Column("date", Date),
                Column("epic", String),
                Column("market", String),
                Column("investments", BigInteger),
                Column("changeToLiabilities", BigInteger),
                Column("changeToAccountReceivables", BigInteger),
                Column("changeToNetincome", BigInteger),
                Column("changeInCash", BigInteger),
                Column("changeToInventory", BigInteger),
                Column("changeToOperatingActivities", BigInteger),
                Column("totalCashflowsFromInvestingActivities", BigInteger),
                Column("totalCashFromFinancingActivities", BigInteger),
                Column("totalCashFromOperatingActivities", BigInteger),
                Column("issuanceOfStock", BigInteger),
                Column("netIncome", BigInteger),
                Column("repurchaseOfStock", BigInteger),
                Column("depreciation", BigInteger),
                Column("dividendsPaid", BigInteger),
                Column("capitalExpenditures", BigInteger),
                Column("netBorrowings", BigInteger),
                Column("effectOfExchangeRate", BigInteger),
                Column("otherCashflowsFromFinancingActivities", BigInteger),
                Column("otherCashflowsFromInvestingActivities", BigInteger),
            )
            meta.create_all(self.engine)
        except Exception as e:
            print(e)

    def createIncomeStatementTable(self):
        try:
            meta = MetaData()
            tab = Table(
                "val_inv_anal_incomesheet",
                meta,
                Column("date", Date),
                Column("epic", String),
                Column("market", String),
                Column("researchDevelopment", BigInteger),
                Column("effectOfAccountingCharges", BigInteger),
                Column("incomeBeforeTax", BigInteger),
                Column("minorityInterest", BigInteger),
                Column("netIncome", BigInteger),
                Column("sellingGeneralAdministrative", BigInteger),
                Column("grossProfit", BigInteger),
                Column("ebit", BigInteger),
                Column("operatingIncome", BigInteger),
                Column("otherOperatingExpenses", BigInteger),
                Column("interestExpense", BigInteger),
                Column("extraordinaryItems", BigInteger),
                Column("nonRecurring", BigInteger),
                Column("otherItems", BigInteger),
                Column("incomeTaxExpense", BigInteger),
                Column("totalRevenue", BigInteger),
                Column("totalOperatingExpenses", BigInteger),
                Column("costOfRevenue", BigInteger),
                Column("totalOtherIncomeExpenseNet", BigInteger),
                Column("discontinuedOperations", BigInteger),
                Column("netIncomeFromContinuingOps", BigInteger),
                Column("netIncomeApplicableToCommonShares", BigInteger),
            )
            meta.create_all(self.engine)
        except Exception as e:
            print(e)

    def Logger(self, file_name):
        formatter = logging.Formatter(
            fmt="%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s",
            datefmt="%Y/%m/%d %H:%M:%S",
        )  # %I:%M:%S %p AM|PM format
        logging.basicConfig(
            filename="%s.log" % (file_name),
            format="%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s",
            datefmt="%Y/%m/%d %H:%M:%S",
            filemode="a",
            level=logging.DEBUG,
        )
        LOG = logging.getLogger()
        LOG.setLevel(logging.DEBUG)

        # console printer
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logging.getLogger().addHandler(screen_handler)

        LOG.info("Logger object created successfully..")
        return LOG

    def cashStatementConversion(self, marketE):
        self.createCashStatementTable()
        anal_file = (
            "/home/colin/development/python/dash-trading/analysis_data/"
            + marketE.name
            + "_cashStatement.txt"
        )
        info = open(anal_file, "r")
        cashStatement = ast.literal_eval(info.read())
        for ticker in cashStatement:
            if cashStatement[ticker] == None:
                logging.getLogger().debug(ticker + " has no data")
                continue

            for bs in cashStatement[ticker]:
                theDate = ""
                for key, value in bs.items():
                    theDate = key
                df = pd.DataFrame.from_dict(bs, orient="index")
                df["date"] = theDate
                df.rename(columns={list(df)[0]: "date"}, inplace=True)
                df["epic"] = ticker.upper()
                df["market"] = marketE.name
                try:
                    df.to_sql(
                        "val_inv_anal_cashsheet",
                        con=BaseHelper.engine,
                        if_exists="append",
                        index=False,
                    )
                    BaseHelper.session.commit()
                except Exception as e:
                    logging.getLogger().exception(str(e))
                    logging.getLogger().debug(ticker + " insert failed")
            print(ticker + " added to val_inv_anal_cashsheet")

    def incomeStatementConversion(self, marketE):
        self.createIncomeStatementTable()
        anal_file = (
            "/home/colin/development/python/dash-trading/analysis_data/"
            + marketE.name
            + "_incomeStatement.txt"
        )
        info = open(anal_file, "r")
        incomeStatement = ast.literal_eval(info.read())
        for ticker in incomeStatement:
            if incomeStatement[ticker] == None:
                logging.getLogger().debug(ticker + " has no data")
                continue

            for bs in incomeStatement[ticker]:
                theDate = ""
                for key, value in bs.items():
                    theDate = key
                df = pd.DataFrame.from_dict(bs, orient="index")
                df["date"] = theDate
                df.rename(columns={list(df)[0]: "date"}, inplace=True)
                df["epic"] = ticker.upper()
                df["market"] = marketE.name
                try:
                    df.to_sql(
                        "val_inv_anal_incomesheet",
                        con=BaseHelper.engine,
                        if_exists="append",
                        index=False,
                    )
                    BaseHelper.session.commit()
                except Exception as e:
                    logging.getLogger().exception(str(e))
                    logging.getLogger().debug(ticker + " insert failed")
            print(ticker + " added to val_inv_anal_incomesheet")

    # read in the analysis files
    # strip out each companies data.
    # Create table (if not present).
    # update table with analysis data
    def balanceSheetConversion(self, marketE):
        self.createBalanceSheetTable()
        anal_file = (
            "/home/colin/development/python/dash-trading/analysis_data/"
            + marketE.name
            + "_balanceSheet.txt"
        )
        info = open(anal_file, "r")
        balanceSheet = ast.literal_eval(info.read())
        dfTickers = pd.read_sql_query(
            "SELECT * FROM public.val_inv_anal_balsheet;", con=BaseHelper.conn
        )

        for ticker in balanceSheet:
            if balanceSheet[ticker] == None:
                continue

            if ticker.lower() in dfTickers["epic"].unique():
                continue

            for bs in balanceSheet[ticker]:
                theDate = ""
                for key, value in bs.items():
                    theDate = key
                df = pd.DataFrame.from_dict(bs, orient="index")
                df["date"] = theDate
                df.rename(columns={list(df)[0]: "date"}, inplace=True)
                df["epic"] = ticker.upper()
                df["market"] = marketE.name
                try:
                    df.to_sql(
                        "val_inv_anal_balsheet",
                        con=BaseHelper.engine,
                        if_exists="append",
                        index=False,
                    )
                    BaseHelper.session.commit()
                except Exception as e:
                    logging.getLogger().debug(str(e))
            print(ticker + " added to val_inv_anal_balsheet")

    # This function adds new records to the corrisponding Value investing analysis table.
    # First check to see if the records exist in the table. If they do then just return and do nothing
    # def addValInv2TableData(ticker, data, tablName):

    def clearTableData(self, marketE, tableName):
        tickers = self.getTickersList(marketE)
        for ticker in tickers:
            lTicker = ticker.ticker.lower()
            try:
                nm = '"' + nm + '"'
                BaseHelper.conn.execute(
                    "DELETE FROM public." + tableName + "WHERE epic=" + nm
                )
                BaseHelper.session.commit()
            except Exception as e:
                logging.getLogger().debug(str(e))

    def updateTableWithMarket(self, marketE):
        tickers = self.getTickersList(marketE)
        for tb in (
            "val_inv_anal_balsheet",
            "val_inv_anal_cashsheet",
            "val_inv_anal_incomesheet",
        ):
            try:
                dfTickers = pd.read_sql_query(
                    "SELECT * FROM public." + tb + ";", con=BaseHelper.conn
                )
                for ticker in tickers:
                    lTicker = ticker.ticker.lower()
                    lTicker = "'" + lTicker + "'"
                    dfTickers["market"][dfTickers["epic"] == lTicker] = marketE.name
                dfTickers.to_sql(
                    tb, con=BaseHelper.engine, if_exists="replace", index=False
                )
            except Exception as e:
                print(str(e))

    # def dropTables(self):
    #     drops=dropables.dt
    #     for drop in drops:
    #         try:
    #             #nm = '"' + nm + '"'
    #             BaseHelper.conn.execute(
    #                 "DROP TABLE "+drop
    #             )
    #             BaseHelper.session.commit()
    #         except Exception as e:
    #             logging.getLogger().debug(str(e))            

if __name__ == "__main__":
    dbc = ValInvDataConversion()
    LOG = dbc.Logger("deb")

    market = markets_enum.s_and_p
    # # dbc.clearTables(market, "val_inv_anal_balsheet")
    dbc.balanceSheetConversion(market)

    # # dbc.clearTables(market, "val_inv_anal_cashsheet")
    dbc.cashStatementConversion(market)

    # # dbc.clearTables(market, "val_inv_anal_incomesheet")
    dbc.incomeStatementConversion(market)

    #dbc.updateTableWithMarket(market)
    #dbc.dropTables()
