# ensure that you already installed yfinance library
# pip install yfinance

import yfinance as yf
import csv
import sys

start = sys.argv[1]
end = sys.argv[2]
interval = sys.argv[3]

t = "TSLA"
cpny = yf.Ticker(t)
cpny_stock = cpny.history(
	start=start, # (data['created_at'].min()).strftime('%Y-%m-%d'),
	end=end, # data['created_at'].max().strftime('%Y-%m-%d'),
	# - valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
	# - default is '1d'
	interval=interval 
).reset_index()

cpny_stock.to_csv("data/stock_data.csv") #.format())


# t = "TSLA"
# cpny = yf.Ticker(t)
# cpny_stock = cpny.history(
# 	start="2021-03-01", # (data['created_at'].min()).strftime('%Y-%m-%d'),
# 	end="2021-04-01", # data['created_at'].max().strftime('%Y-%m-%d'),
# 	# - valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
# 	# - default is '1d'
# 	interval="1d" 
# ).reset_index()
