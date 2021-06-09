############### extract TSLA tweets from long-term data  ##################

# import sys
import pyspark
from pyspark import SparkConf
from pyspark.sql import SparkSession
# from pyspark.sql.functions import col, lit, substring,concat
from pyspark.sql.functions import min as sparkMin
import pyspark.sql.functions as F
import pandas as pd
import datetime
# from pyspark.sql.window import Window

spark = SparkSession \
    .builder \
    .appName("Stock Price Prediction") \
    .getOrCreate()

# =================================================
# 1. Process tweets data
# - filter out TSLA tweet id
# - join tweet id table with tweet content table
# =================================================

ID = spark.read.csv("data/tweets/Company_Tweet.csv", header=True)
ID = ID.filter(ID.ticker_symbol == "TSLA") \
	.drop("ticker_symbol")

Tweets = spark.read.csv("data/tweets/Tweet.csv", header=True)

# only use post after [year]
year = [2018,2019,2020,2021]

for i in range(len(year)-1):
	starttime = int((datetime.datetime(year[i],1,1) - datetime.datetime(1970,1,1)).total_seconds())
	endtime = int((datetime.datetime(year[i+1],1,1) - datetime.datetime(1970,1,1)).total_seconds())
	t = Tweets.filter((starttime < Tweets.post_date) & (Tweets.post_date< endtime)) \
			.join(ID, "tweet_id")	\
			.write.format('csv') \
		    .option('header',True) \
		    .mode('overwrite') \
		    .option('sep',',') \
		    .save('data/long_term_tweets_{}'.format(year[i]))

