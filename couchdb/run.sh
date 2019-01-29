docker stop couch
docker rm couch

docker run -d \
-e COUCHDB_USER=admin -e COUCHDB_PASSWORD='Ultra password 5000.' \
-v ~/Users/Shared/couchdb/data:/opt/couchdb/data \
-p 5984:5984 --network vaas2_vaasnet --ip 172.16.66.4 \
--name couch couchdb
