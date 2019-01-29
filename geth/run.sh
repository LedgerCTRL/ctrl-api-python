docker stop geth-node
docker rm geth-node

# run geth on dev chain
docker run -dit -p 30303:30303 -p 8546:8546 -p 8545:8545 --network vaas2_vaasnet --ip 172.16.66.3 \
--name geth-node \
-v /Users/Shared/gethdata:/root/.ethereum ethereum/client-go \
--rpc --rpcaddr 0.0.0.0 --ws --wsaddr 0.0.0.0 \
--rpcapi eth,web3,net,web3,personal \
--dev --datadir "/root/.ethereum"
