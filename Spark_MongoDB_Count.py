from pymongo import MongoClient
import os 
import json 

path = "/Users/lookphanthavong/Documents/VisualStudioCode/BDEA/Twitter/Follower_Relationship.json"
print("Lade Daten ... \n")
with open(path) as jsonfile:
    read_file = json.load(jsonfile)


# ID = read_file[9]["_id"]
ID = 364971269
print(ID)

client = MongoClient("mongodb://0.0.0.0:27017/")
db = client["test"]
test_collection = db["promi_tweets"]
x = test_collection.find_one({"_id":ID})
print(x)
Count_Follower = len(x["Tweets"])
print(Count_Follower)
