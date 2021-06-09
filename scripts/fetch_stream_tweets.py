# ensure that you already installed yfinance library
# pip install tweepy
import logging
import json
import tweepy
import time
import sys
from progressbar import *
from datetime import datetime,timezone
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

#Variables that contains the user credentials to access Twitter API 
access_token = "950545014542741504-uToPAGQNxW5GWYcEhVmSl1HZiRYbKVM"
access_token_secret = "Eg6CJE9nkTPIHGTa0m1WBGUhd7GqZjMyTUkVsBnql5NxZ"
consumer_key = "w01zE83UD0sGGWukEgpUitoep"
consumer_secret = "tARyuJvmBIZlCrgygzfgY1SmzpymLYMJcZL5o4eQ7JVf72U403"

# keywords = ['#tesla', '#spacex', '#elon', '#elonmusk', '#autopilot', 'tesla', 'elon', 'spacex, autopilot']
keywords = ['#teala', 'tesla']

class StdOutListener(StreamListener):

    def on_data(self, data):
        print(data)
        return True

    def on_error(self, status):
        print(status)

if __name__ == '__main__':

    logger = logging.getLogger("Fetch Script")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("Fetch Script Running...")

    # parse arguments
    if len(sys.argv) != 3:
        print("Wrong Number of Arguments")
        sys.exit(1)

    runtime = int(sys.argv[1]) # minute
    output_path = str(sys.argv[2])
    sys.stdout = open(output_path, 'w')

    logger.info("Runtime: " + str(runtime) + " seconds.")
    logger.info("Output to: " + output_path)

    # add listener
    l = StdOutListener()

    # create stream
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l, tweet_mode='extended')

    # filter on key words
    try:
        stream.filter(track=keywords, is_async=True)
    except:
        sys.exit()
    
    progress = ProgressBar()
    for i in progress(range(runtime)):
        time.sleep(1)
        
    stream.disconnect()
