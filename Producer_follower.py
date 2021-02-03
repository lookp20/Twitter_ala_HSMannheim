from kafka import KafkaProducer
from time import sleep
from json import dumps
import json
import logging
import numpy as np
import pandas as pd
from tqdm import tqdm
path = "/Users/lookphanthavong/Documents/VisualStudioCode/BDEA/Twitter/Follower_Relationship.json"
print("Lade Daten ... \n")
with open(path) as jsonfile:
    read_file = json.load(jsonfile)

#read_file_copy = read_file[:10] 
print("Daten sind geladen ...\n")

print("Beginne LogIn in Kafka ...\n")
logging.basicConfig(level=logging.INFO)

producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda x:json.dumps(x).encode("utf-8"))
print("Starte Datenübermittlung ...\n")
for item in tqdm(read_file):
    producer.send('follower_relationship', item)
print("Datenübermittlung abgeschlossen ...")
#     sleep(5)






