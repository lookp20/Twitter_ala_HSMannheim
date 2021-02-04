from flask import Flask, render_template, url_for, redirect, request, session
from werkzeug.utils import secure_filename
import os, sys, stat, operator
from pymongo import MongoClient
from datetime import datetime
from random import randint
from kafka import KafkaProducer
from time import sleep
from json import dumps
import json
import logging
import numpy as np
import pandas as pd
from tqdm import tqdm


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/', methods=['GET', 'POST'])
def enter_ID():
    if request.method == "POST":
        session["ID"] = request.form["text"]
        client = MongoClient("mongodb://0.0.0.0:27017/")
        db = client["test"]
        test_collection = db["follower_relationship"]
        x = test_collection.find_one({"_id":str(session.get("ID"))})
        if x == None:
            msg = "Tippe eine andere ID ein !!!"
            return render_template("home2.html", msg=msg)   
        else:
            tweets_collection = db["tweets_for_"+ str(session.get("ID"))]
            # collect_tweets = []
            # for y in tweets_collection.find({}, {"_id":0, "author": 1, "Tweets": 0 }):
            #     collect_tweets += [y]
            # print(collect_tweets)
            # print(len(collect_tweets[0]))
            # ind= 0
            # Name = y["author"]
            # content = y["Tweets"][ind]["content"]
            # Likes = str(y["Tweets"][ind]["number_of_likes"])
            # Shares = str(y["Tweets"][ind]["number_of_shares"])
            # DateTime = y["Tweets"][ind]["date-time"]
            # TweetID = str(y["Tweets"][ind]["Tweet_id"])
            # return render_template("home3.html", Name=Name, content=content, Likes=Likes, Shares=Shares, DateTime=DateTime, TweetID=TweetID)
    
        return render_template("home.html")
    return render_template("home.html")



@app.route("/follower", methods=['GET', 'POST'])
def follower():
    if request.method == "GET":
        sequence = session.get("ID")
        client = MongoClient("mongodb://0.0.0.0:27017/")
        db = client["test"]
        test_collection = db["follower_relationship"]
        x = test_collection.find_one({"_id":str(session.get("ID"))})
        Count_Follower = len(x["Followers"])
        if Count_Follower >= 20:
            list_follower = x["Followers"][:20]
        else:
            list_follower = x["Followers"]
        
        Count_Following = len(x["Following"])
        if Count_Following >= 20:
            list_following = x["Following"][:20]
        else:
            list_following = x["Following"]
    return render_template("follower_prototyp.html", list1=list_follower, list2=list_following, Count_Follower=Count_Follower, Count_Following=Count_Following)


@app.route("/tweets", methods=['GET', 'POST'])
def tweets():
    if request.method == "GET":
        Input_ID = session.get("ID")
        client = MongoClient("mongodb://0.0.0.0:27017/")
        db = client["test"]
        test_collection = db["promi_tweets"]
        x = test_collection.find_one({"_id":int(Input_ID)})
        if x == None:
            text = "Du hast keine eigenen Tweets :-C"
            return render_template("tweets.html", text=text)
        else:
            content = []
            Likes = []
            Shares = []
            DateTime = []
            kleine_Liste = []
            Große_Liste = []
            for i in range(2):
                ind = i
                Name = x["author"]
                content += [x["Tweets"][ind]["content"]]
                Likes += [str(x["Tweets"][ind]["number_of_likes"])]
                Shares += [str(x["Tweets"][ind]["number_of_shares"])]
                DateTime += [x["Tweets"][ind]["date-time"]]
                TweetID = str(x["Tweets"][ind]["Tweet_id"])
                kleine_Liste += [Name, content, Likes, Shares, DateTime]
                print("Kleine Liste ->", kleine_Liste)
                Große_Liste +=[kleine_Liste]
                print("Große Liste ->", Große_Liste)
            return render_template("tweets.html", Große_Liste=Große_Liste)

            #return render_template("tweets.html", Name=Name, content=content, Likes=Likes, Shares=Shares, DateTime=DateTime, TweetID=TweetID)
    return render_template("tweets.html")


@app.route("/tweetsSend", methods=['GET', 'POST'])
def tweetsSend():
    if request.method == "POST":
        session["AbsenderID"] = request.form["text"]
        session["Tweet"] = request.form["textfield"]
        client = MongoClient("mongodb://0.0.0.0:27017/")
        db = client["test"]
        test_collection = db["follower_relationship"]
        x = test_collection.find_one({"_id":str(session.get("AbsenderID"))})
        promi_tweets_collection = db["promi_tweets"]
        y = promi_tweets_collection.find_one({"_id":int(session.get("AbsenderID"))})
        print(type(y["Tweets"]))
        if x == None:
            msg = "Tippe eine andere ID ein !!!"
            return render_template("tweetsSend2.html", msg=msg)   
        else:
            dict_kafka = {
                "content": session.get("Tweet"),
                "number_of_likes": 0,
                "number_of_shares":0,
                "date-time": str(datetime.now()),
                "Tweet_id": randint(100,1000000000000)
            }
            y["Tweets"][0].update(dict_kafka)
            logging.basicConfig(level=logging.INFO)
            producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda x:json.dumps(x).encode("utf-8"))
            print("Starte Datenübermittlung ...\n")
            producer.send('promi_tweets', y)
            sleep(5)
            print("Datenübermittlung abgeschlossen ...")
        return render_template("tweetsSend.html")
    return render_template("tweetsSend.html")





if __name__ == "__main__":
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(debug=True)