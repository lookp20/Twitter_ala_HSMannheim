from pyspark.sql import SparkSession

input_uri = "mongodb://mongo:27017/test.promi_tweets"
output_uri = "mongodb://mongo:27017/test.promi_tweets"

spark = SparkSession\
    .builder\
    .appName("Promi_Tweets")\
    .config("spark.mongodb.input.uri",input_uri)\
    .config("spark.mongodb.output.uri",output_uri)\
    .getOrCreate()

people = spark.createDataFrame([("Bilbo Baggins",  50), ("Gandalf", 1000), ("Thorin", 195), ("Balin", 178), ("Kili", 77),
   ("Dwalin", 169), ("Oin", 167), ("Gloin", 158), ("Fili", 82), ("Bombur", None)], ["name", "age"])

people.write.format("mongo").mode("append").save()

