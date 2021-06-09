#!/bin/bash

# Run scripts iter times for runtime secs
let iter=$1
let runtime=$2
date=$3

mkdir data/tweet_raw_${date}
mkdir data/tweet_parsed_${date}

baseFetchOutpath="data/tweet_raw_${date}/tweet_data_raw_"
baseReadInpath="data/tweet_raw_${date}/tweet_data_raw_"
baseReadOutpath="data/tweet_parsed_${date}/tweet_data_parsed_"

for i in `seq 1 $iter`;
do 
python scripts/fetch_stream_tweets.py $runtime ${baseFetchOutpath}${i};
echo "Fetch Job ${i} Done."
done

for i in `seq 1 $iter`;
do
python scripts/read_stream_tweets.py ${baseReadInpath}${i} ${baseReadOutpath}${i};
echo "Read Job ${i} Done."
done

echo "Data Collection Done."

# python3 scripts/extract_stock_realtime.py
# echo "Stock Collection Done."

# python3 scripts/process_join_data.py
# echo "Data Join Done."
