#!/bin/bash

set -e
(
if lsof -Pi :27017 -sTCP:LISTEN -t >/dev/null ; then
    echo "Please terminate the local mongod on 27017"
    exit 1
fi
)

echo "Building the MongoDB Kafka Connector"
(
cd ..
./gradlew clean createConfluentArchive
echo -e "Unzipping the confluent archive plugin....\n"
unzip -d ./build/confluent ./build/confluent/*.zip
find ./build/confluent -maxdepth 1 -type d ! -wholename "./build/confluent" -exec mv {} ./build/confluent/kafka-connect-mongodb \;
)

if ! [ -f jar_libs/mongo-spark-connector_2.12-3.0.0-assembly.jar ]; then
    echo "Downloading mongo-spark-connector"
    curl -L --create-dirs 'https://search.maven.org/remotecontent?filepath=org/mongodb/spark/mongo-spark-connector_2.12/3.0.0/mongo-spark-connector_2.12-3.0.0-assembly.jar' -o jar_libs/mongo-spark-connector_2.12-3.0.0-assembly.jar
fi

if ! [ -f jar_libs/spark-streaming-kafka-0-10-assembly_2.12-3.0.0.jar ]; then
    echo "Downloading spark-streaming-kafka"
    curl -L --create-dirs 'https://search.maven.org/remotecontent?filepath=org/apache/spark/spark-streaming-kafka-0-10-assembly_2.12/3.0.0/spark-streaming-kafka-0-10-assembly_2.12-3.0.0.jar' -o jar_libs/spark-streaming-kafka-0-10-assembly_2.12-3.0.0.jar
fi

if ! [ -f jar_libs/spark-sql-kafka-0-10_2.12-3.0.0.jar ]; then
    echo "Downloading spark-sql-kafka"
    curl -L --create-dirs 'https://search.maven.org/remotecontent?filepath=org/apache/spark/spark-sql-kafka-0-10_2.12/3.0.0/spark-sql-kafka-0-10_2.12-3.0.0.jar' -o jar_libs/spark-sql-kafka-0-10_2.12-3.0.0.jar
fi

echo "Starting docker ."
docker-compose up -d --build

function clean_up {
    echo -e "\n\nSHUTTING DOWN\n\n"
    curl --output /dev/null -X DELETE http://localhost:8083/connectors/datagen-pageviews || true
    curl --output /dev/null -X DELETE http://localhost:8083/connectors/mongo-sink || true
    curl --output /dev/null -X DELETE http://localhost:8083/connectors/mongo-source || true
    docker-compose exec mongo /usr/bin/mongo --eval "db.dropDatabase()"
    docker-compose down
    if [ -z "$1" ]
    then
      echo -e "Bye!\n"
    else
      echo -e $1
    fi
}

sleep 5
echo -ne "\n\nWaiting for the systems to be ready.."
function test_systems_available {
  COUNTER=0
  until $(curl --output /dev/null --silent --head --fail http://localhost:$1); do
      printf '.'
      sleep 2
      let COUNTER+=1
      if [[ $COUNTER -gt 30 ]]; then
        MSG="\nWARNING: Could not reach configured kafka system on http://localhost:$1 \nNote: This script requires curl.\n"

          if [[ "$OSTYPE" == "darwin"* ]]; then
            MSG+="\nIf using OSX please try reconfiguring Docker and increasing RAM and CPU. Then restart and try again.\n\n"
          fi

        echo -e $MSG
        clean_up "$MSG"
        exit 1
      fi
  done
}

test_systems_available 8082
test_systems_available 8083

trap clean_up EXIT

echo -e "\nConfiguring the MongoDB ReplicaSet.\n"
docker-compose exec mongo /usr/bin/mongo --eval '''if (rs.status()["ok"] == 0) {
    rsconf = {
      _id : "rs0",
      members: [
        { _id : 0, host : "mongo:27017", priority: 1.0 },
      ]
    };
    rs.initiate(rsconf);
}

rs.conf();'''

echo -e "\nKafka Topics:"
curl -X GET "http://localhost:8082/topics" -w "\n"

echo -e "\nKafka Connectors:"
curl -X GET "http://localhost:8083/connectors/" -w "\n"

echo -e "\nAdding promi_tweets:"
curl -X POST -H "Content-Type: application/json" --data '
  { "name": "promi_tweets",
    "config": {
      "connector.class": "io.confluent.kafka.connect.datagen.DatagenConnector",
      "kafka.topic": "promi_tweets",
      "quickstart": "promi_tweets",
      "key.converter": "org.apache.kafka.connect.json.JsonConverter",
      "value.converter": "org.apache.kafka.connect.json.JsonConverter",
      "value.converter.schemas.enable": "false",
      "producer.interceptor.classes": "io.confluent.monitoring.clients.interceptor.MonitoringProducerInterceptor",
      "max.interval": 200,
      "iterations": 10000000,
      "tasks.max": "1"
}}' http://localhost:8083/connectors -w "\n"

sleep 5

echo -e "\nAdding MongoDB Kafka Sink Connector for the 'promi_tweets' topic into the 'test.promi_tweets' collection:"
curl -X POST -H "Content-Type: application/json" --data '
  {"name": "mongo-sink1",
   "config": {
     "connector.class":"com.mongodb.kafka.connect.MongoSinkConnector",
     "tasks.max":"1",
     "topics":"promi_tweets",
     "connection.uri":"mongodb://mongo:27017",
     "database":"test",
     "collection":"promi_tweets",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.json.JsonConverter",
     "value.converter.schemas.enable": "false"
}}' http://localhost:8083/connectors -w "\n"

sleep 2
echo -e "\nAdding MongoDB Kafka Source Connector for the 'test.promi_tweets' collection:"
curl -X POST -H "Content-Type: application/json" --data '
  {"name": "mongo-source1",
   "config": {
     "tasks.max":"1",
     "connector.class":"com.mongodb.kafka.connect.MongoSourceConnector",
     "connection.uri":"mongodb://mongo:27017",
     "topic.prefix":"mongo",
     "database":"test",
     "collection":"promi_tweets"
}}' http://localhost:8083/connectors -w "\n"


# ---------------------------------------------------------------------

echo -e "\nAdding follower_relationship:"
curl -X POST -H "Content-Type: application/json" --data '
  { "name": "follower_relationship",
    "config": {
      "connector.class": "io.confluent.kafka.connect.datagen.DatagenConnector",
      "kafka.topic": "follower_relationship",
      "quickstart": "follower_relationship",
      "key.converter": "org.apache.kafka.connect.json.JsonConverter",
      "value.converter": "org.apache.kafka.connect.json.JsonConverter",
      "value.converter.schemas.enable": "false",
      "producer.interceptor.classes": "io.confluent.monitoring.clients.interceptor.MonitoringProducerInterceptor",
      "max.interval": 200,
      "iterations": 10000000,
      "tasks.max": "1"
}}' http://localhost:8083/connectors -w "\n"

echo -e "\nAdding MongoDB Kafka Sink Connector for the 'follower_relationship' topic into the 'test.relationship' collection:"
curl -X POST -H "Content-Type: application/json" --data '
  {"name": "mongo-sink",
   "config": {
     "connector.class":"com.mongodb.kafka.connect.MongoSinkConnector",
     "tasks.max":"1",
     "topics":"follower_relationship",
     "connection.uri":"mongodb://mongo:27017",
     "database":"test",
     "collection":"follower_relationship",
     "key.converter": "org.apache.kafka.connect.storage.StringConverter",
     "value.converter": "org.apache.kafka.connect.json.JsonConverter",
     "value.converter.schemas.enable": "false"
}}' http://localhost:8083/connectors -w "\n"

sleep 2
echo -e "\nAdding MongoDB Kafka Source Connector for the 'test.follower_relationship' collection:"
curl -X POST -H "Content-Type: application/json" --data '
  {"name": "mongo-source",
   "config": {
     "tasks.max":"1",
     "connector.class":"com.mongodb.kafka.connect.MongoSourceConnector",
     "connection.uri":"mongodb://mongo:27017",
     "topic.prefix":"mongo",
     "database":"test",
     "collection":"follower_relationship"
}}' http://localhost:8083/connectors -w "\n"

#------------------------------------------------------------

docker-compose exec mongo /usr/bin/mongo --eval "db.createCollection('follower_relationship')"
docker-compose exec mongo /usr/bin/mongo --eval "db.createCollection('promi_tweets')"



# sleep 2
# echo -e "\nKafka Connectors: \n"
# curl -X GET "http://localhost:8083/connectors/" -w "\n"

# echo "Looking at data in 'db.pageviews':"
# docker-compose exec mongo1 /usr/bin/mongo --eval 'db.pageviews.find()'

sleep 2
echo -e "\nKafka Connectors: \n"
curl -X GET "http://localhost:8083/connectors/" -w "\n"

# echo "Looking at data in 'db.follower_relationship':"
# docker-compose exec mongo1 /usr/bin/mongo --eval 'db.follower_relationship.find()'


echo -e '''

==============================================================================================================
Examine the topics in the Kafka UI: http://localhost:9021 or http://localhost:8000/
  - The `pageviews` topic should have the generated page views.
  - The `mongo.test.pageviews` topic should contain the change events.
  - The `test.pageviews` collection in MongoDB should contain the sinked page views.

Examine the collections:
  - In your shell run: docker-compose exec mongo1 /usr/bin/mongo
==============================================================================================================

Use <ctrl>-c to quit'''

read -r -d '' _ </dev/tty
