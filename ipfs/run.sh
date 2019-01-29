docker stop ipfs-node
docker rm ipfs-node

docker run -dit --rm --name ipfs-node \
  -v /tmp/ipfs-docker-staging:/export -v /tmp/ipfs-docker-data:/data/ipfs \
  -p 8080:8080 -p 4001:4001 -p 5001:5001 \
  --network vaas2_vaasnet --ip 172.16.66.5 \
  ipfs/go-ipfs:v0.4.17
