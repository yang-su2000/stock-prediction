- Idea

Our hypothesis the stock market price trend is highly related to the public impression towards the companys,
and social medias like Twitter is a common place where people express their opinions.

Our investigation target is the Tesla Inc,

Use real-time tweets sent by user to get s sense of the public impression on stock market, and try to quantify it by assigning scores to each tweets, then run LSTM model to train the scores generated on the timeline, to predict a future trend of stock market.

1. Retrieve Data

Use Twitter stream api to retrieve real-time tweets, store as json format
Filter by keywords, we focus on ‘Tesla’, ‘ElonMusk’, ‘SpaceX’…
Slice the data by minute, get 60 data setsParse Data

2. Parse Data

3. Collect Result

For each data set, we collect a score result like this.

- Prediction

- Methodology

1. Big Data source: Real-time social media data filtered by keywords
2. Python scripts to retrieve data using twitter apis, loads data into json format
3. Use Spark Framework to perform MapReduce job on the time-sliced data sets
4. Use LSTM model to train and make prediction
5. Compared with ground truth data to see if our trend is correct

- Implementation
  // To Do

- Result
  // To Do
