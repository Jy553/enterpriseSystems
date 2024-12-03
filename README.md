# enterpriseSystems
Repository for Enterprise Systems Task One

Group 11: Jamie Young, Liam McClelland, Kamron Blythe-Stone

## How to run rabbit MQ
run the following to start the rabbitmq server in the background. 
```shell
docker-compose up -d
```
To stop RabbitMQ, run
```shell
docker-compose stop
```

## How to run App
First ensure RabbitMQ is running. Then continue with steps below.

Ensure you have all the required python dependencies by running the following command:
```shell
pip install -r requirements.txt
```

1. Start the server worker (note, this is for proof of concept of the application running. )
```shell
python server.py
```

2. In another terminal window, start the app

```shell
python smart_meter_client.py
```



