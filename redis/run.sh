docker stop redis
docker rm redis

docker run -d \
--ip 172.16.66.6 --network vaas2_vaasnet -p 6379:6379 \
-v /Users/Shared/redis:/data \
--name redis redis
