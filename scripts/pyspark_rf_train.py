import pyspark
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import OneHotEncoder, StringIndexer, VectorAssembler
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

spark = SparkSession \
    .builder \
    .appName("Stock Price SparkSession") \
    .getOrCreate()

df = spark.read.csv("data/data_processed_0412/*.csv", header=True, inferSchema=True)
numericCols = ['favorite_count', 'retweet_count', 'author_followers_count', \
    'author_listed_count', 'author_statuses_count', 'author_friends_count', \
    'author_favourites_count', 'sentiment_polarity', 'sentiment_subjectivity']
hashtagCols = [column for column in df.columns if (column[0] == 'h' and column[1] == 't')]
numericCols.extend(hashtagCols)

df.select(numericCols)
df.cache()
df.printSchema()
train, test = df.randomSplit([0.7, 0.3], seed = 123)
print("Training Dataset Count: " + str(train.count()))
print("Test Dataset Count: " + str(test.count()))

assembler = VectorAssembler(handleInvalid="skip")\
    .setInputCols(numericCols)\
    .setOutputCol("features")
train_mod01 = assembler.transform(train)

print("first few lines of transformed training data...")
print(train_mod01.limit(5).toPandas())

train_mod02 = train_mod01.select("features","Trend")
all_mod01 = assembler.transform(df)
all_mod02 = all_mod01.select("id","features")
test_mod01 = assembler.transform(test)
test_mod02 = test_mod01.select("id","features")

# train
rfClassifer = RandomForestClassifier(labelCol = "Trend", numTrees = 10)
pipeline = Pipeline(stages = [rfClassifer])
paramGrid = ParamGridBuilder()\
   .addGrid(rfClassifer.maxDepth, [1, 2, 4, 8, 12, 16, 20])\
   .addGrid(rfClassifer.minInstancesPerNode, [1, 2, 4])\
   .build()
evaluator = MulticlassClassificationEvaluator(labelCol = "Trend", predictionCol = "prediction", metricName = "accuracy")
# 5 folds cv
crossval = CrossValidator(estimator = pipeline,
                          estimatorParamMaps = paramGrid,
                          evaluator = evaluator,
                          numFolds = 5)
# final model
cvModel = crossval.fit(train_mod02)
print("best cv prediction accuracy by all 'paramGrid' metrics")
print(cvModel.avgMetrics)

# predict
prediction = cvModel.transform(all_mod02)
print("first few lines of prediction...")
print(prediction.limit(5).toPandas())
final_pred = prediction.select("id","prediction")
final_pred.toPandas().to_csv('data/data_prediction/predict_rf.csv',index=False)