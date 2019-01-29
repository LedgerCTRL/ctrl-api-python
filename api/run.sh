docker stop vaas2-api
docker stop vaas2_api_1 
docker rm vaas2-api

docker run -it -p 8088:8088 --network vaas2_vaasnet --ip 172.16.66.2 --name vaas2-api vaas2-api
