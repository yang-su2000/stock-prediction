# stock-prediction

#### How to get Long-term Data

only processed dataset `long_term_processed_[year]` was uploaded

Here is how the dataset was created:

##### 1- Download Dataset from Kaggle

1. get your `kaggle.json` , put it in `~/.kaggle/kaggle.json`

2. install kaggle

   ```
   pip3 install kaggle --user
   export PATH=~/.local/bin:$PATH
   ```

3. download the dataset

   ```
   kaggle datasets download -d omermetinn/tweets-about-the-top-companies-from-2015-to-2020
   unzip tweets-about-the-top-companies-from-2015-to-2020.zip data/
   ```

the original dataset contains data from 2015 to 2020, but here we are only using data from 2018 to 2020

##### 2- Extract tweets

run `long_term_extract_tweets.py`

```
python3 scripts/long_term_extract_tweets.py
```

- due to java heap space limitation, we have to split the data to corresponding year and output them separately.
- this scripts is hard-coded to output data for 2018 to 2020
- **output**: in `data/long_term_tweets_{year}`

##### 3- Extract stock prices

run `long_term_extract_stock.py`

```
python3 scripts/long_term_extract_stock.py [start] [end]
python3 scripts/long_term_extract_stock.py 2018 2019
```

- run this script to extract monthly stock price from in [start] year to [end] year
- in our case, just run it 3 times, with `start` in [2018-2020], and `end = start+1`
- **output**: in `data/long_term_stock_{year}`

##### 4- Process data

run `long_term_process.py`

```
python3 scripts/long_term_process.py [target-year]
python3 scripts/long_term_process.py 2018
```

- run this script to process & join data to a trainable state for `target-year`
- in our case, just run it 3 times, with `target-year` in [2018-2020]
- **output**: in `data/long_term_processed_{year}`

##### 5- Add sentiment score

run  `long_term_sentiment.py`

```
python3 scripts/long_term_sentiment.py [target-year]
python3 scripts/long_term_sentiment.py 2018
```

- run this script to process & join data to a trainable state for `target-year`
- in our case, just run it 3 times, with `target-year` in [2018-2020]
- **output**: in `data/long_term_sentiment_{year}`
   

#### Scripts

All scripts should be running under Python 3.6.

- `twitter.sh`

  ```
  python3 -m pip install tweepy
  python3 -m pip install progressbar
  python3 -m pip install pandas
  python3 -m pip install textblob
  python3 -m pip install emojis

  chmod +x twitter.sh
  ./twitter.sh [iteration] [runtime] [date]
  ```

  1. Use `progressbar` library to display script running progess.
  2. Set command line arg `iteration` to adjust how many iterations to run.
  3. Set command line arg `runtime` to adjust how long to run in seconds for each iteration.
  4. Set command line arg `date` to adjust the date of running.
  5. Raw tweet jsons are stored in `data/tweet_raw_[date]/*`.
  6. Processed csv files are stored in `data/tweet_parsed_[date]/*`.

  ```
  # If we fetch 6 hours of real-time data, 30 min each set on 13rd April, then run twitter.sh:
  $ ./twitter.sh 12 1800 0413
  ```

- `fetch_stream_tweets.py`

  ```
  pip3 install tweepy
  python3 scripts/fetch_stream_tweets [runtime in seconds] [output_path]
  ```

  uses `tweepy` library to extract streaming tweeter data for a certain period of time

- `read_stream_tweets.py`

  ```
  pip3 install textblob
  python3 scripts/read_stream_tweets [input_path] [output_path]
  ```

  uses `pandas` library to read and parse the tweeter data and outputs a csv file
  uses `textblob` library to access the sentiment score of tweet content

- `extract_stock.py`

  uses `yfinance` library to extract stock data for Tesla

  ```
  pip3 install yfinance
  python3 extract_stock.py [start-date] [end-date] [interval]
  ```

  for example, to extract monthly stock data from Oct 2020 to Dec 2020

  ```
  python3 extract_stock.py 2020-10-01 2020-12-01 1mo
  ```

  - in the script, change `ticker_name` to desired company name in the script

  - valid  `interval` values: 

    ```
    1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    ```

  - valid `start`, `end` values

    ```
    [year-month-day]: 2020-10-01
    ```

  - Run in main directory `/stock_prediction`, and output `stock_data.csv` file will be in `/data` folder

- `pandas_predict.py`

  - debug purpose, use it to test ml framework without pyspark

- `pyspark_predict.py`

  - change `global_setup` part to debug

- `process_join_data.py`

  ```
  python3 process_join_data.py [target_date]
  python3 process_join_data.py 0409
  ```

  - process tweets for hashtags. outputted to `data/tweet_processed_{target_date}/` folder as a csv file
  - process tweets and stock data, and join them to be outputted to `data/data_processed/` folder as a csv file
  - should be run in main directory
  - make sure you have `data/stock_data.csv` before running

  note:

  - `window_size=10` : look at stock price changes 10 minutes after the tweet's create time
  - `trend`: 1 represents increasing, -1 represents decreasing, 0 otherwise

- `pyspark_rf_train.py`

  - take input of `data/data_processed/*.csv` as training (and testing, for now) data
  - train 5 folds cv random forest model on numerical data
    - customize 1: change `max_trees`, max amount of random forests generated
    - customize 2: change `maxDepth`, max depth of each random forest
    - customize 3: change `minInstancesPerNode`, minimum distance of each subnode, currently calculated using Gini index
  - output to `data/data_prediction/`
  - run in main directory

- `cnn_train.py`

  - install anaconda
  - install tensorflow in anaconda
  - take input of `data/data_processed/*.csv` as training data
    - customize 1: change `BATCH_SIZE`, number of data processed in one iteration
    - customize 2: change `epochs`
  - run in main directory

- `lstm_train.py`

  - currently using manual one-hot encoding, next: embedding text
  - run in main directory

#### Features

- `Sentiment_Score`

- `Emoji_Score`

