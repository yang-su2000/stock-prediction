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
import time
from pyspark.sql.window import Window
from pyspark.sql.types import IntegerType,StringType

spark = SparkSession \
    .builder \
    .appName("Stock Price Prediction") \
    .getOrCreate()

target_year = sys.argv[1]

# ============================================================
# 1. convert from epoch string (1483272000) to month (2015-06)
# ============================================================

def epoch_to_time(epoch):
    return time.strftime('%Y-%m', time.localtime(epoch))

udf_epoch_to_time = F.udf(epoch_to_time, StringType())

tweets = spark.read.csv("data/long_term_tweets_"+target_year+"/*.csv", header=True)
tweets = tweets.withColumn("post_date",tweets.post_date.cast(IntegerType())) \
    .withColumn("post_month",udf_epoch_to_time("post_date"))

# ============================================================
# 2. Process Stock data
# ============================================================

window_size = 1

stock = spark.read.csv("data/long_term_stock_"+target_year+".csv", header=True) \
    .withColumn("Month",substring("Date", 1, 7)) \
    .withColumn("Average",(col("Open") + col("High") + col("Low") + col("Close")) / lit(4)) \
    .select(col("Month"),col("Average"))

y_window = Window.partitionBy().orderBy(stock.Month)
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
        .select(col("Month"),col("Trend")) \
        .filter(substring("Month",1,4)==target_year)

# =================================================
# 3. Join stock data with corresponding tweets data
# =================================================

joined_data = tweets.join(stock, tweets.post_month==stock.Month) \
    .drop("Month") \
    .write.format('csv') \
    .option('header',True) \
    .mode('overwrite') \
    .option('sep',',') \
    .save('data/long_term_processed_{}'.format(target_year))


