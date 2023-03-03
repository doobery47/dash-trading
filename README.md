# candlestick-screener
web-based technical screener for candlestick patterns using TA-Lib, Python, and Flask

## Video Tutorials for this repository:

* Candlestick Pattern Recognition - https://www.youtube.com/watch?v=QGkf2-caXmc
* Building a Web-based Technical Screener - https://www.youtube.com/watch?v=OhvQN_yIgCo
* Finding Breakouts - https://www.youtube.com/watch?v=exGuyBnhN_8

githun token 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

market data: https://www.marketwatch.com/investing/index/mcx/download-data?countrycode=uk&mod=mw_quote_tab

downloaddatapartial?startDate=08/03/2022 00:00:00&endDate=09/02/2022 23:59:59&dateRange=D30&frequency=P1D&CsvDownload=true&DownloadPartial=false&NewDates=false"

TODO

3. get info and positions on invidual sectors.
    get current positions from https://www.lse.co.uk/share-prices/sectors/
    would need to scrape this data. 
    Should be able to use https://www.fidelity.co.uk/shares/ftse-100/ to scrape
    off the sectors for each of the ftse stocks.
    --DOW to be done
    --FTSE 100 and 250 have some tickers with no sector values
4. Could multithread some of the pages ie stock updates.
5. Value investing. Add a chart that compairs all the stock. Make this a line chart.
    Good source of info for combine is https://www.youtube.com/watch?v=NNu1DjWcYeY 
11. Portfolio - Add option to make it either current or old
12. Portfolio - create current with current prices.
13. Portfolio - Add share prices as well.
14. Portfolio - Add Sandras to old and new but keep in seprate table. Add Grand total
15. Portfolio - Have another go at Plotly
16. Look at calnder and look for end of year etc..
17. Dash-Stock_update page. cant see the tickers being updated. The status list cant be updated due to 
    using the same id in in 2 callback Outputs. Have a look at 
    https://community.plotly.com/t/multiple-callbacks-for-an-output/51247 to resolve this.

improvements for dash version.
2. Portfolio
    Equities/Historic/Colin has an error
3. Candlestick analysis. THis now works to a fashion. We run the candlestick patten against the 
    data and retieve the Bullish ad bearish results for the whole graph, but when we display the graph
    it gives no indication which dates had these bearish/bullish swings. So with this version we need to 
    dislpay the table of data and intract with the graph. Or display another line on the graph with the 
    markers (dates) imbeded in the line.
    We need to have another look at the graph. shold include one running avarage and one subplot.


Stratagy

What has an impact on the share price?
1. The fed and the BOE - mainly the interest rates. 
    - How and what are the impacts.
    - how can quantify this
2. Change in the ftse/nasdaq/dow prices.
    - as the price of a share has is an integral impact (small or large) in the movemnt of the market value
      then there is a direct correlation between the share price and market price. 
      There is one one the YouTube videos describe this.
3. 

NOTES on looking for company investment indicators.
- Warron buffett
    - All stocks are bits of companies and that his how you should look at a stock
    - VALUE THE BUSINESS TO DETERMINE WHAT IT IS WORTH.
        How do you value an business and how do you corralate this with the market price????
    - Margen of safety
    - Observations you look for in a business.
        -Enduring compedative advantage
            -A company shoud have a moat around itself. Could be a patent, location etc. Need to protect its
            market against compeditors. 
        - a company that is so good it can be run by an idiot. But a company should be run
          honoust and trustworthy people
        - A price that is fair
        - when picking a company look a lot of factors discard companies and get rid of those.

NOTES from Peter Lynch
    - Put stokes into categories. This helps you decide what questions to ask about a company
    - If a company is a slow grower and you have made enough profit then it maybe time to sell.
    - Companies can be determined as fast grower, slow grower, cyclical, asset plays, turnarounds
    - slow to moderate grower will have a earnings growth of 3% to 15% a year
    - signs *** steady earmings growth
      *** rising dividends
      cyclical
      *** wait for things to get better before investing.
      *** pick a stromg company, survive when the cycle goes down, good cash flow and low debt
      Turnarounds - batterened, haited, forgotted about

    - Earnigs and net income. If they are increasing then the company is doing someting right. 
    --Warron Buffet looking for.
    -- In the income statement
        - Gross margin (https://www.investopedia.com/terms/g/grossmargin.asp) Companies use gross margin, gross profit, and gross profit margin to measure how their production costs relate to their revenues. The higher the number-the more comoany sells then the greater the profitability. Look for compnies that exceed 35% over a number of years.
        - Net margin. 20% and above
    -- Looking for the balance sheet
        - Retained earnings. This is a reflection of reinvestment. Return on equity (total equity compaired to net income) can be used to measure how well retained earning are being used. 
        - Long term debt to should be low or should be going down over a number of years.
    -- Cash flow statement
        - Capital expenditure (capital expenditure/Net income). This should be low as possible. Less than 25% is very good and below 50% is 
        acceptable. However you have to take into consideraton one of amounts for large expansions
    -- When to sell
        - sell to reinvest in another opertunity.
        - Company is loosing its competative advantage (ie newspapers)
        - During a crazy bull market. if the PE ratio is above 40


Notes to self.
    - what the sector that the company is in. This can have an impact on the dynaics and grouth. Also use the
      other companies in sector to compare performs ie PE ratio


READING.

Look at https://github.com/snehilvj/dash-mantine-components. Looks like more controls for Dash.
Look at https://github.com/matplotlib/mplfinance. Diplaying finacial data


Morgan Stanley - Global Brands (MSJD.SG)
Stuttgart - Stuttgart Delayed price. Currency in EUR
AXA Framlington American Growth Fund Z Inc (0P0000VKOV.L)
Fundsmith Equity I Acc (0P0000RU81.L)
LSE - LSE Delayed price. Currency in GBp (0.01 GBP)


SIPS
Morgan Stanley - Global Brands (MSJD.SG)
Stuttgart - Stuttgart Delayed price. Currency in EUR
Jupiter Global Managed L Acc (0P0000JTV4.L)
Jupiter Global Managed I Acc (0P0000U20I.L)
LSE - LSE Delayed price. Currency in GBp (0.01 GBP)
AXA Framlington American Growth Fund Z Inc (0P0000VKOV.L)
Jupiter Global Managed I Inc (0P0000X9VN.L)
LSE - LSE Delayed price. Currency in GBp (0.01 GBP)

Shares

Microsoft (MSFT) 43 shares
Whitbread (WTB) 81 shares

Sandra
Troy trojan global income 
Jupiter global managed fund


shiller Excess cape yeald messure 
forward P/E

Portfolio:
     - List of current investments.
     - upto date prices etc on the investments
     - graph of each investment
     - Analysis on each of the shares, What??

regularMarketPrice

/home/colin/development/python/dash-trading/pages/PortfolioHelper.py

https://github.com/tcbegley/dash-rq-demo/blob/main/README.md


features
Still of stocks that have made money year on year over 2 or 3 years


