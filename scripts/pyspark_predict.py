import pyspark
from pyspark import SparkConf
from pyspark.sql import SparkSession

# from keras import optimizers
# from keras.models import Sequential
# from keras.layers import Dense, LSTM, Dropout, GRU
# from pyspark.ml.evaluation import RegressionEvaluator

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# global_setup
show_description = True
show_fig = True
SPLIT_SEED = 12345

spark = SparkSession \
    .builder \
    .appName("Stock Price Prediction") \
    .getOrCreate()

if show_description:
    print("sparkContext:")
    print(spark.sparkContext.getConf().getAll())

# df = spark.read.csv("tweetsParsed.csv", header=True)
stock_data = spark.read.csv("../data/stock_data.csv", header=True)

# combine high, low, open, close price to an average stock price
# result in a df containing columns ['Datetime','Avg']
avg_price = stock_data[['Open','High','Low','Close']].mean(axis=1)
stock_data = pd.concat([stock_data[['Datetime']],avg_price], axis=1)
stock_data.columns = ['Datetime','Avg']

if show_description:
    print("dataframe type:", type(df))
    print("dataframe schema:")
    df.printSchema()

if show_fig:
    print("dataframe header(5):")
    df.show(5)
    print("dataframe summary:")
    df.describe().show()

'''
    To Do
'''
def load_data(path):
    
    raise NotImplementedError

def generate_features(df):

    raise NotImplementedError

def train_test_split(df):

    train_set, test_set = df.randomSplit([0.8, 0.2], seed=SPLIT_SEED)

    return train_set, test_set

def model_train(df):

    raise NotImplementedError

def model_evaluation(df):

    raise NotImplementedError

def model_selection(df):

    raise NotImplementedError
