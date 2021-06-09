# =================================================
# Process stock and tweets data
# =================================================
import sys
import pyspark
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, substring,concat
from pyspark.sql.functions import min as sparkMin
import pyspark.sql.functions as F
import pandas as pd
from pyspark.sql.types import IntegerType
# import datetime, time
from pyspark.sql.window import Window

spark = SparkSession \
    .builder \
    .appName("Stock Price Prediction") \
    .getOrCreate()

# global_setup
# show_description = True
# show_fig = True
# SPLIT_SEED = 12345

# if show_description:
#     print("sparkContext:")
#     print(spark.sparkContext.getConf().getAll())

#################  Get commandline args  ################
# target_date = "0409"
target_date = sys.argv[1]
threshold = 1

relative_phrase = ["crypto", "eth", "crypto", "elon", "btc", "musk"]

# =================================================
# 1. Process tweets data
# - created_at column has format: 2021-04-07 17:37:23
# - round it to 2021-04-07 17:37:00 as a join key with stock data
# =================================================

# data by day: 2021-04-07
tweets = spark.read.csv("data/tweet_parsed_"+target_date+"/*.csv", header=True) \
    .withColumn("created_at",concat(substring("created_at", 1, 17),lit("00"))) 

tweets = tweets.withColumn("hashtags", F.lower("hashtags"))

    # - clean the hashtag, split it to array of strings
    # - explode to new rows of hashtags
    # - to lower case 
    # - group by hashtag name
    # - filter out ones that occurs more than [threshold] times
ht = tweets \
    .withColumn("hashtags", F.regexp_replace("hashtags", "\\[", "")) \
    .withColumn("hashtags", F.regexp_replace("hashtags", "\\]", "")) \
    .withColumn("hashtags", F.regexp_replace("hashtags", "\\'", "")) \
    .withColumn("hashtags", F.split(col("hashtags"), "\\,"))

########## each row represents a hashtag
ht_dict =  ht.select(col("hashtags")) \
    .select("hashtags",F.explode_outer("hashtags")) \
    .select(col("col").alias("hashtag"))
ht_dict = ht_dict.filter(ht_dict.hashtag != "") \
    .groupBy("hashtag").count() \
    .select(col("hashtag"),col("count").alias("occurance"))
ht_dict = ht_dict.filter(ht_dict.occurance>=lit(threshold)) \
    .withColumn("hashtag", F.trim(col("hashtag")))

relative_ht = list(ht_dict.select('hashtag').toPandas()['hashtag'])

###---------------------------------------------------------------
for i, word in enumerate(relative_ht):
    name = "ht_"+ str(i)
    tweets = tweets.withColumn(name, \
        F.when(tweets.hashtags.contains(lit(word)), 1 ) \
        .otherwise( 0 ))

# =================================================
# 2. Calculate average stock data
# - combine high, low, open, close price to an average stock price
# - result in a df containing columns ['Datetime','Trend']
# =================================================

window_size = 10

stock = spark.read.csv("data/stock_data.csv", header=True) \
    .withColumn("Average",(col("Open") + col("High") + col("Low") + col("Close")) / lit(4)) \
    .select(col("Datetime"),col("Average")) \
    .withColumn("Datetime",substring("Datetime", 1, 19))

y_window = Window.partitionBy().orderBy(stock.Datetime)
    # create Post_price column for each Datetime
    # corresponds to creted_at_minute col for tweets data
stock = stock.withColumn("Post_price", F.lead(stock.Average, window_size) \
    .over(y_window))

# calculate the diff, and the trend => 1 for up, 0 for down, 2 for same/null values
stock = stock.withColumn("Trend", \
        F.when(F.isnull(stock.Average - stock.Post_price), 2) \
        # increasing
        .when((stock.Average < stock.Post_price), 1) \
         # decreasing
        .when((stock.Average > stock.Post_price), 0) \
        .otherwise(2)) \
        .select(col("Datetime"),col("Trend"))

# =================================================
# 3. Join stock data with corresponding tweets data
# =================================================

joined_data = tweets.join(stock, tweets.created_at==stock.Datetime) \
    .drop("Datetime") \
    .write.format('csv') \
    .option('header',True) \
    .mode('overwrite') \
    .option('sep',',') \
    .save('data/data_processed_{}'.format(target_date))