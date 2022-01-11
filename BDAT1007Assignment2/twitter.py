#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 11:20:36 2021

@author: Emma
"""

#Import libraries
import tweepy as tw
from pymongo import MongoClient
import credentials
import pandas as pd

# Get the mongoclient
client = MongoClient(credentials.Mongo.mongo_access)
db = client['Media']
collection = db['Twitter']


class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = tw.OAuthHandler(credentials.twitterCredential.api_key, credentials.twitterCredential.api_secret)
        auth.set_access_token(credentials.twitterCredential.access_token, credentials.twitterCredential.access_token_secret)
        return auth


class TwitterClient():
     #Get authorization from Twitter
    def __init__(self,twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = tw.API(self.auth)
        self.twitter_user = twitter_user
       
    #Grab tweets until reaches the required number of tweets
    #Save those tweets' id,created time,content,sources and account name to dictionary
    def get_tweets(self,num_tweets):
        id_str=[]
        created_at=[]
        text=[]
        source=[]
        screen_name=[]
        
        for tweet in tw.Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
           id_str.append(tweet.id_str)
           created_at.append(tweet.created_at)
           text.append(tweet.text)
           source.append(tweet.source)
           screen_name.append(tweet.user.screen_name)
           
        return {"id":id_str,"created_at":created_at,"contents":text,"source":source,"account_name":screen_name}

#Creat a new object with my twitter id and give it the number of tweets to grab
myTweet=TwitterClient("EmmaEmmaGuo").get_tweets(100)

print(myTweet)

#insert the records to Mongodb
df=pd.DataFrame(myTweet)
collection.delete_many({})
collection.insert_many(df.to_dict('records'))




