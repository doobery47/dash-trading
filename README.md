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
1. Get news and info on indivisual stocks
2. Get market current values and data
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
6. Home - double up graphs.
7. Home - "index displayed rather than "Date"
8. Home - Option to make graph either candel or line
9. Home - Cache so that the graphs data is not updated.
10. Home - Cache the graphs
11. Portfolio - Add option to make it either current or old
12. Portfolio - create current with current prices.
13. Portfolio - Add share prices as well.
14. Portfolio - Add Sandras to old and new but keep in seprate table. Add Grand total
15. Portfolio - Have another go at Plotly
16. Look at calnder and look for end of year etc..
17. Dash-Stock_update page. cant see the tickers being updated. The status list cant be updated due to 
    using the same id in in 2 callback Outputs. Have a look at 
    https://community.plotly.com/t/multiple-callbacks-for-an-output/51247 to resolve this.


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

