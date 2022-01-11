#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 12:25:33 2021

@author: Emma
"""
from flask import Flask, render_template, url_for,request
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
import credentials
import twitter
import reddit
from datetime import datetime
import praw

app = Flask(__name__)

#Connect MongoDB
app.config["MONGO_DBNAME"]= 'Media'
app.config["MONGO_URI"] = credentials.Mongo.mongo_access
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

#Web app for reddit
@app.route('/Reddit', methods=['GET','POST'])
def Reddit():
    #make a request to post new reddit and insert to MongoDB
    if request.method =='POST':
        title = str(request.form["RedditTitle"])
        content = str(request.form["RedditContents"])
        reddit_api = reddit.RedditClient().reddit
        subreddit=reddit_api.subreddit('u_'+ credentials.reddit().login_username)
        new_reddit = subreddit.submit(title,content)
        ts = int(new_reddit.created_utc)
        collection = mongo.db.Reddit
        collection.insert_one({
                                "id":new_reddit.id,
                                "created_at":datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'),#convert the unix to datetime
                                "title":new_reddit.title,
                                "contents":new_reddit.selftext,
                                "account_name":new_reddit.author.name})
        return render_template('index.html')
    
#Web app for twitter    
@app.route('/Twitter', methods=['GET','POST'])
def Twitter():
    #make a request to post new tweets and insert to MongoDB
    if request.method =='POST':
        msg = request.form['Tweets']
        status = twitter.TwitterClient().twitter_client.update_status(msg)
        collection = mongo.db.Twitter
        collection.insert_one({
                                "id":status.id_str,
                                "created_at":status.created_at,
                                "contents":status.text,
                                "source":status.source,
                                "account_name":status.user.screen_name})
        return render_template('index.html')

#run flask
if __name__ =="__main__":
    app.run(debug=True)

