from textblob import TextBlob
import logging
import json
import sys
import tweepy
import emojis
import pandas as pd
from progressbar import *

#Variables that contains the user credentials to access Twitter API 
access_token = "950545014542741504-uToPAGQNxW5GWYcEhVmSl1HZiRYbKVM"
access_token_secret = "Eg6CJE9nkTPIHGTa0m1WBGUhd7GqZjMyTUkVsBnql5NxZ"
consumer_key = "w01zE83UD0sGGWukEgpUitoep"
consumer_secret = "tARyuJvmBIZlCrgygzfgY1SmzpymLYMJcZL5o4eQ7JVf72U403"

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_row', 1000)


if __name__ == '__main__':

    logger = logging.getLogger("Read Script")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("Read Script Running...")

    # parse arguments
    if len(sys.argv) != 3:
        print("Wrong Number of Arguments")
        sys.exit(1)

    # set input path
    input_path = str(sys.argv[1])
    output_path = str(sys.argv[2])
    sys.stdout = open(output_path, 'w')

    logger.info("Reading file: " + input_path)
    logger.info("Output csv to: " + output_path + ".csv")

    # authorization of consumer key and consumer secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # open file
    tweet_ids = []
    try:
        tweets_file = open(input_path, "r")
    except IOError:
        print("Error: can't open file")

    # read into json format
    for line in tweets_file:
        try:
            id = json.loads(line)['id']
            tweet_ids.append(id)
        except:
            continue

    emoji_dict = {} # emoji, sub_group
    emoji_pos = ["face-affection", "face-smiling", "face-tongue", "emotion", "transport-air"]
    emoji_neg = ["face-sleep", "face-unwell", "face-concerned", "face-negative"]

    emoji_df = pd.read_csv("data/emoji_df.csv")
    for index, row in emoji_df.iterrows():
        if row['group'] == 'Smileys & Emotion' or row['group'] == 'Travel & Places':
            emoji_dict[row['emoji']] = row['sub_group']

    def getSentimentScore(content):
        testimonial = TextBlob(content)
        return {
            'Polar': round(testimonial.sentiment.polarity, 3), 
            'Subject': round(testimonial.sentiment.subjectivity, 3)
        }

    def getEmojiScore(content):
        # emoji_lst = emoji_str.join(emojis.get(content))
        emoji_lst = list(emojis.get(content))
        score = 0
        for emoji in emoji_lst:
            if emoji in emoji_dict:
                # print(emoji_lst)
                # print(emoji_dict[emoji])
                for e in emoji_pos: 
                    if str(emoji_dict[emoji]) == e: score += 1 
                for e in emoji_neg: 
                    if str(emoji_dict[emoji]) == e: score -= 1 
        return score

    tweet_dict = {}
    # tweet_dict[''] = []
    tweet_dict['truncated'] = []
    tweet_dict['retweet_count'] = []
    tweet_dict['favorite_count'] = []
    tweet_dict['author_followers_count'] = []
    tweet_dict['author_listed_count'] = []
    tweet_dict['author_lang'] = []
    tweet_dict['author_statuses_count'] = []
    tweet_dict['author_friends_count'] = []
    tweet_dict['author_favourites_count'] = []
    tweet_dict['author_location'] = []
    tweet_dict['mentions_names'] = []
    tweet_dict['hashtag_indices'] = []
    tweet_dict['hashtags'] = []
    # tweet_dict['retweet_truncated'] = []
    # tweet_dict['retweet_favorite_count'] = []
    # tweet_dict['retweet_author_followers_count'] = []
    # tweet_dict['retweet_author_listed_count'] = []
    # tweet_dict['retweet_author_lang'] = []
    # tweet_dict['retweet_author_statuses_count'] = []
    # tweet_dict['retweet_author_friends_count'] = []
    # tweet_dict['retweet_author_favourites_count'] = []
    # tweet_dict['retweet_author_location'] = []
    tweet_dict['lang'] = []
    tweet_dict['created_at'] = []
    tweet_dict['place'] = []
    tweet_dict['text'] = []
    tweet_dict['sentiment_polarity']= []
    tweet_dict['sentiment_subjectivity']= []
    tweet_dict['emoji_score']= []

    # extract info from raw data
    progress = ProgressBar()
    size = 0
    logger.info("Number of tweets to process: " + str(len(tweet_ids)))
    for i in progress(range(len(tweet_ids))):
        id = tweet_ids[i]
        try:
            status = api.get_status(id)
            # tweet_dict[''].append()
            tweet_dict['truncated'].append(status.truncated)
            tweet_dict['retweet_count'].append(status.retweet_count)
            tweet_dict['favorite_count'].append(status.favorite_count)
            tweet_dict['author_followers_count'].append(status.author.followers_count)
            tweet_dict['author_listed_count'].append(status.author.listed_count)
            tweet_dict['author_lang'].append(status.author.lang)
            tweet_dict['author_statuses_count'].append(status.author.statuses_count)
            tweet_dict['author_friends_count'].append(status.author.friends_count)
            tweet_dict['author_favourites_count'].append(status.author.favourites_count)
            tweet_dict['author_location'].append(status.author.location)
            entities_mentions_names = []
            for user in status.entities['user_mentions']:
                entities_mentions_names.append(user['name'])
            entities_hashtag_indices = []
            entities_hashtags = []
            for hashtag in status.entities['hashtags']:
                entities_hashtag_indices.append(hashtag['indices'][0])
                entities_hashtags.append(hashtag['text'])
            tweet_dict['hashtag_indices'].append(entities_hashtag_indices)
            tweet_dict['hashtags'].append(entities_hashtags)
            tweet_dict['lang'].append(status.lang)
            tweet_dict['created_at'].append(status.created_at)
            tweet_dict['place'].append(status.place)
            tweet_dict['text'].append(status.text)
            tweet_dict['sentiment_polarity'].append(getSentimentScore(str(status.text))['Polar'])
            tweet_dict['sentiment_subjectivity'].append(getSentimentScore(str(status.text))['Subject'])
            tweet_dict['emoji_score'].append(getEmojiScore(status.text))
            size += 1
        except:
            continue

    # print info
    if 0:
        i = 0
        while i < size:
            # = tweet_dict[''][i]
            truncated =                  tweet_dict['truncated'][i]
            retweets =                   tweet_dict['retweet_count'][i]
            likes =                      tweet_dict['favorite_count'][i]
            author_followers =           tweet_dict['author_followers_count'][i]
            author_listed =              tweet_dict['author_listed_count'][i]
            author_lang =                tweet_dict['author_lang'][i]
            author_statuses =            tweet_dict['author_statuses_count'][i]
            author_friends =             tweet_dict['author_friends_count'][i]
            author_favourites =          tweet_dict['author_favourites_count'][i]
            author_location =            tweet_dict['author_location'][i]
            hashtag_indices =            tweet_dict['hashtag_indices'][i]
            hashtags =                   tweet_dict['hashtags'][i]
            lang =                       tweet_dict['lang'][i]
            created_at =                 tweet_dict['created_at'][i]
            place =                      tweet_dict['place'][i]
            text =                       tweet_dict['text'][i].replace(",", " ").replace("\n", ". ") # remove line breakers
            sentiment_polarity =         tweet_dict['sentiment_polarity'][i]
            sentiment_subjectivity =     tweet_dict['sentiment_subjectivity'][i]
            emoji_score =                      tweet_dict['emoji_score'][i]

            # add to output
            print(truncated, retweets, likes, author_followers, author_listed, author_lang, author_statuses, \
                author_friends, author_favourites, author_location, hashtag_indices, hashtags, lang, \
                created_at, place, text, sentiment_polarity, sentiment_subjectivity, emoji_score)
            i += 1

    # output to csv
    else:
        tweets = []
        i = 0
        while i < size:
            tweet = []
            tweet.append(i)
            # tweet.append(tweet_dict[''][i])
            tweet.append(tweet_dict['truncated'][i])
            tweet.append(tweet_dict['retweet_count'][i])
            tweet.append(tweet_dict['favorite_count'][i])
            tweet.append(tweet_dict['author_followers_count'][i])
            tweet.append(tweet_dict['author_listed_count'][i])
            tweet.append(tweet_dict['author_lang'][i])
            tweet.append(tweet_dict['author_statuses_count'][i])
            tweet.append(tweet_dict['author_friends_count'][i])
            tweet.append(tweet_dict['author_favourites_count'][i])
            author_location = tweet_dict['author_location'][i]
            tweet.append(author_location if not author_location is None else author_location)
            tweet.append(tweet_dict['hashtag_indices'][i])
            tweet.append(tweet_dict['hashtags'][i])
            tweet.append(tweet_dict['lang'][i])
            tweet.append(tweet_dict['created_at'][i])
            place = tweet_dict['place'][i]
            tweet.append(place if not place is None else place)
            tweet.append(tweet_dict['text'][i].replace(",", " ").replace("\n", ". ")) # remove line breakers
            tweet.append(tweet_dict['sentiment_polarity'][i])
            tweet.append(tweet_dict['sentiment_subjectivity'][i])
            tweet.append(tweet_dict['emoji_score'][i])
            tweets.append(tweet)
            i += 1

        # add colname to dataframe
        df = pd.DataFrame(tweets, columns=['id', 'truncated', 'favorite_count', 'retweet_count', \
            'author_followers_count', 'author_listed_count', 'author_lang', 'author_statuses_count', \
            'author_friends_count', 'author_favourites_count', 'author_location', 'hashtag_indices', \
            'hashtags', 'lang', 'created_at', 'place', 'text', 'sentiment_polarity', 'sentiment_subjectivity', 'emoji_score'])
        df.to_csv(output_path + ".csv", index=False)
    