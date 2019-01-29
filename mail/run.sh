docker stop maildev
docker rm maildev

docker container run -d -p 1080:80 -p 25:25 --ip 172.16.66.7 --network vaas2_vaasnet --name maildev djfarrelly/maildev
