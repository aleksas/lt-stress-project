# Stress container

## Build
```sh
docker build -t aleksas/lt-stress-serve:0.0.2 -f lt-stress-serve.Dockerfile .
```

## Run stress model server 
```sh
docker run -p 8500:8500 -p 8501:8501  aleksas/lt-stress-serve:0.0.2
```

# Query terminal container
## Build

```sh
docker build -t aleksas/lt-stress-query:0.0.2 -f lt-stress-query.Dockerfile .
```

## Run stress query terminal 
```sh
docker run  aleksas/lt-stress-query:0.0.2
```


# Compose
Run `docker-compose up` to run a flask web service. 

Open browser to [localhost:8080](http://localhost:8080) 
