import os
import tweepy
import spacy
from .models import DB, Tweet, User
import spacy


key = os.getenv('TWITTER_API_KEY')
secret = os.getenv('TWITTER_API_SECRET_KEY')

twitter_auth = tweepy.OAuthHandler(key, secret)
twitter = tweepy.API(twitter_auth)

nlp = spacy.load('my_model')

def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector

def add_or_update_user(username):
    try:
        twitter_user = twitter.get_user(screen_name=username)
        db_user = User.query.get(username=username)
        if not db_user:
            db_user = User(id=twitter_user.id, username=username)
            DB.session.add(db_user)
        
        tweets = twitter_user.timeline(
            count=200, exclude_replies=True, include_rts=False, tweet_mode='extended'
        )

        for tweet in tweets:
            db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:300])
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print(f'Error processing {username}: {e}')
        raise e


    DB.session.commit()