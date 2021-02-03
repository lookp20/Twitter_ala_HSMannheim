from flask import Flask, render_template, url_for, redirect, request, session
from werkzeug.utils import secure_filename
import os, sys, stat, operator
from pymongo import MongoClient

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
    return render_template("follower.html", list1=list_follower, list2=list_following, Count_Follower=Count_Follower, Count_Following=Count_Following)


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
        
            ind = 625
            Name = x["author"]
            content = x["Tweets"][ind]["content"]
            Likes = str(x["Tweets"][ind]["number_of_likes"])
            Shares = str(x["Tweets"][ind]["number_of_shares"])
            DateTime = x["Tweets"][ind]["date-time"]
            TweetID = str(x["Tweets"][ind]["Tweet_id"])
          
            return render_template("tweets.html", Name=Name, content=content, Likes=Likes, Shares=Shares, DateTime=DateTime, TweetID=TweetID)
    return render_template("tweets.html")


@app.route("/tweetsSend")
def tweetsSend():
    return render_template("tweetsSend.html")





if __name__ == "__main__":
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(debug=True)