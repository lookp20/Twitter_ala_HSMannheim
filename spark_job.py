import json
from datetime import datetime
from pymongo import MongoClient
from pyspark.sql import SparkSession

my_spark = SparkSession \
    .builder \
    .master("local[*]") \
    .appName("Twitter Job") \
    .config('spark.jars.packages', 'org.apache.spark:spark-streaming_2.12:3.0.0') \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0') \
    .getOrCreate()

df = my_spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "192.168.56.4:9092") \
    .option("subscribe", "python_test") \
    .load()

df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

def processRow(row):
    kafka_message = json.loads(row.asDict()["value"])
    tweets = kafka_message["Tweets"]
    new_tweet = sorted(tweets, key=lambda x: datetime.strptime(x["date-time"], "%d/%m/%Y %H:%M"), reverse=True)[0]  # get the newest tweet 21/12/2016 23:05

    # query all followers
    client = MongoClient("mongodb://192.168.56.4:27017")
    test_db = client["test"]
    collection = test_db["follower_relationship"]
    twitter_user = collection.find_one({"_id": str(kafka_message['_id'])})
    user_followers = twitter_user["Followers"]

    # add the tweet to the followers timelines
    for follower in user_followers:
        feed_collection = test_db[f"tweets_for_{int(follower)}"]
        feed_collection.insert_one(new_tweet)

def process_df(df, epoch_id):
    df.show()
    df.foreach(processRow)

query = df.writeStream.foreachBatch(process_df).start()
query.awaitTermination()
