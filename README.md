# CTRL API
>*previously VaaS API*

*Swagger-gen’d python3-flask HTTP REST API for blockchain itemization using IPFS & Ethereum.*

## Introduction
CTRL API uses docker and docker-compose to build and run the entire backend.

Background services include **couchdb, go-ipfs, go-ethereum (geth).**

The primary **api** ties them all together with a sleek little REST API.

> Note: *All services are exposed to localhost, so use a firewall!*


## GET Started
CTRL needs virtually no configuration. Just send it.

### Install Dependencies
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Run tha trap
```git clone https://github.com/brocksmedley/ctrl-api
cd vaas2
docker-compose build
docker-compose up```

### Configure dotenv file
Set the following variables in a file called `.env` in the root directory of this repository.
```COUCHDB_USER=admin
COUCHDB_PASS=Password!```

### Configure dotenv file
Set the following variables in a file called `.env` in the root directory of this repository.
```
COUCHDB_USER=admin
COUCHDB_PASS=Password!
```

### Configure DB
1. Make an admin account at `localhost:5984/_utils/#/setup`.

   Make sure it matches the username/password in your frontend.

2. Create the `users` database at `http://localhost:5984/_utils/#/_all_dbs`.

### Use it!
Local Gateways

name | gateway | .md requires 3 columns for tables
--- | --- | ---
couchDB | [`http://localhost:5984`](http://localhost:5984) | nice
IPFS | [`http://localhost:8080`](http://localhost:8080/ipfs) | nice
geth | [`http://localhost:8545`](http://localhost:8545) | nice
CTRL API | [`http://localhost:8088`](http://localhost:8088) | nice

Copyright VaaS Technologies, Inc. 2019

This source code may be used under the GPL License. See license.txt for details.
