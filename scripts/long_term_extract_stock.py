import yfinance as yf
import csv
import sys

start_year = sys.argv[1]
end_year = sys.argv[2]
interval = "1mo"

t = "TSLA"
cpny = yf.Ticker(t)
cpny_stock = cpny.history(
	start=start_year+"-01-01",
	end=end_year+"-01-01",
	interval=interval 
).reset_index()

cpny_stock.to_csv("data/long_term_stock_{}.csv".format(start_year))

