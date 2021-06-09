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
from pyspark.sql.types import DoubleType, ArrayType, IntegerType
from textblob import TextBlob

spark = SparkSession \
    .builder \
    .appName("Stock Price Prediction") \
    .getOrCreate()

target_year = sys.argv[1]

def getSentimentScore(content):
    testimonial = TextBlob(content)
    polarity = round(float(testimonial.sentiment.polarity), 3)
    subjectivity = round(float(testimonial.sentiment.subjectivity), 3)
    return [polarity,subjectivity]

udf_get_sentiment = F.udf(getSentimentScore, ArrayType(DoubleType()))

tweets = spark.read.csv("data/long_term_processed_"+target_year+"/*.csv", header=True)
tweets = tweets.withColumn("sentiment", udf_get_sentiment("body"))
tweets = tweets.withColumn("polarity", tweets.sentiment.getItem(0)) \
	.withColumn("subjectivity", tweets.sentiment.getItem(1)) \
	.drop("sentiment", "body", "tweet_id", "writer", "post_date", "post_month")

tweets = tweets.withColumn("Trend",tweets.Trend.cast(IntegerType()))
tweets = tweets.withColumn("comment_num",tweets.comment_num.cast(IntegerType()))
tweets = tweets.withColumn("retweet_num",tweets.comment_num.cast(IntegerType()))
tweets = tweets.withColumn("like_num",tweets.comment_num.cast(IntegerType()))	\
	.write.format('csv') \
    .option('header',True) \
    .mode('overwrite') \
    .option('sep',',') \
    .save('data/long_term_sentiment_{}'.format(target_year))


