import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../data/stock_data_TSLA.csv")
print(type(df))
print(df.head())

plt.figure(figsize = (10, 5))
plt.plot(range(df.shape[0]),(df['Low']+df['High'])/2.0)
plt.xticks(range(0,df.shape[0],100),df['Date'].loc[::100],rotation=45)
plt.xlabel('Date',fontsize=18)
plt.ylabel('Mid Price',fontsize=18)
plt.show()

all_data_len = len(df)
high_prices = df['High']
low_prices = df['Low']
mid_prices = (high_prices+low_prices)/2.0

train_data = mid_prices[:int(all_data_len/2)]
test_data = mid_prices[int(all_data_len/2):]
