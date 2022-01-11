#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 12:58:38 2021

@author: Emma
"""

import praw
import credentials
from pymongo import MongoClient
import pandas as pd
from datetime import datetime

# Get the mongoclient
client = MongoClient(credentials.Mongo.mongo_access)
db = client['Media']
collection = db['Reddit']

#Authenticate
class RedditAuthenticator():
    def authenticate_reddit_app(self):
        client_id = credentials.reddit().client_id
        secret_token = credentials.reddit().secret_token
        username = credentials.reddit().login_username
        password = credentials.reddit().login_password

        reddit = praw.Reddit(client_id= client_id,
                     client_secret= secret_token, password=password,
                     user_agent='MediaHelper', username=username,check_for_async=False)
        return reddit

class RedditClient():
    #Get authorization from Reddit
    def __init__(self,reddit_user=None):
        self.reddit = RedditAuthenticator().authenticate_reddit_app()
        self.reddit_user = reddit_user
    
    def get_reddit(self,num_reddit=None):       
        id_str=[]
        created_utc=[]
        title=[]
        selftext=[]
        author=[]
        for submission in self.reddit.redditor(self.reddit_user).submissions.top(limit=num_reddit):
            id_str.append(submission.id)
            #convert unix to readable datetime
            ts = int(submission.created_utc)
            created_utc.append(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
            title.append(submission.title)
            selftext.append(submission.selftext)
            author.append(submission.author.name)
            
        return {"id":id_str,"created_at":created_utc,"title":title,"contents":selftext,"account_name":author}
        
reddit = RedditClient("Emma_Moon11").get_reddit()
print(reddit)

#insert the records to Mongodb
df=pd.DataFrame(reddit)
collection.delete_many({})
collection.insert_many(df.to_dict('records'))
