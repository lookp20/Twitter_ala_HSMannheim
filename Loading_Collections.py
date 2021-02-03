from pymongo import MongoClient
# from bson.objectid import ObjectId
# from bson.son import SON
import json
import pandas as pd 
import os

# Stelle Verbindung zur DB her
client = MongoClient("mongodb://0.0.0.0:27017/")
# Kontrolliere existierende DBs
all_dbs = client.list_database_names()

test_db = client["test"]
list_path = os.listdir("/Volumes/LOOK_USB_C/Tweets_Collection")
tweets_collection = list_path[500:550]

for item in tweets_collection:
    Collection = test_db[item[:-5]]
    with open("/Volumes/LOOK_USB_C/Tweets_Collection/" + item) as jf:
        file_data = json.load(jf)
    Collection.insert_one(file_data)
   

    


# df_mapped = pd.read_csv("/Users/lookphanthavong/Documents/VisualStudioCode/BDEA/Twitter/df_mapped_id.csv")
# df_mapped = df_mapped.drop(["row"], axis=1)

# with open("/Users/lookphanthavong/Documents/VisualStudioCode/BDEA/Twitter/Promi_tweets.json") as jf:
#     PT_file = json.load(jf)

# with open("/Users/lookphanthavong/Documents/VisualStudioCode/BDEA/Twitter/Follower_Relationship.json") as jf:
#     FR_file = json.load(jf)



# def generate_tweets_list(input_id):
#     tweets_list = []
#     for item in FR_file[input_id]["Following"]:
#         if item in df_mapped["id"].values:
#             ind = df_mapped[df_mapped["id"]== item]["author"].values[0]
#             tweets_list += list(filter(lambda PT_file: PT_file['author'] == ind, PT_file))
#     tweets_dict = {"_id":FR_file[input_id]["_id"],"tweets_for_landing_page":tweets_list}   
#     return tweets_dict

# for i in range(len(FR_file)):
#     tweets_collection = test_db["tweets_for_"+str(i)]
#     tweets_dict = generate_tweets_list(i)
#     tweets_collection.insert_one(tweets_dict)


