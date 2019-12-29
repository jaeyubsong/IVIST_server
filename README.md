# IVIST server

One paragraph description to go



## Getting Started

Let's set up the environment

### Prerequisites

- Docker
- Access server via ssh
- (Optional: Add local forwarding to port 5000 to access flask backend directly)
```
$ ssh USERNAME@"SERVER_IP_ADDRESS" -L localhost:5000:localhost:5000
```

### Setting up the environment
- Build docker image
```
$ git clone https://github.com/jsong0327/IVIST_server.git
$ cd IVIST_server
$ docker-compose build --no-cache
```

### Run docker environment
- start docker image with container
```
$ CURRENT_UID=$(id -u):$(id -g) docker-compose up
```




### Useful commands
- access mongoDB with shell
```
$ docker exec -it simpleflaskapp_mongo_1 mongo
```

- access mongoDB with bash
```
$ docker exec -it simpleflaskapp_mongo_1 bash
```

- View containers
```
$ docker container ls -a
```

- Remove containers
```
$ docker container rm "container_name or id"
```

- View images
```
$ docker images
```


- Remove images
```
$ docker rmi "image_name or id"
```

- Export mongodb data
```
$ mongodump --db database_name --collection collection_name
```
- Copy file from container to host
```
docker cp <container id>:/source/file/path/in/container /destination/on/host
```
  
- Import mongodb data
```
$ mongorestore --db database_name path_to_bson_file
```


### Permission errors for 'mondoData' folder

- Access root account
```
$ ssh ROOT_USERNAME@"SERVER_IP_ADDRESS"
```
- Locate mongoData folder
```
$ ssh cd /home/USERNAME/SOMEWHERE_IN_YOUR_ACCOUNT
```
- Change folder permission
```
$ sudo chown -R $(id -u USERNAME):$(id -g USERNAME) ./mongoData
```

