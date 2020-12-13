# Stress container

## Build
```sh
docker build -t aleksas/lt-stress-serve:0.0.2 -f lt-stress-serve.Dockerfile .
```


## Run stress model server 
```sh
docker run -p 8500:8500 -p 8501:8501  aleksas/lt-stress-serve:0.0.2
```

# Query terminal

## Dependencies

```sh
pip install tensor2tensor
pip install tensorflow-serving-api
```

## Run query terminal
```sh
t2t-query-server   --server=localhost:8500   --servable_name=stress-transformer-lite-v1   --problem=translate_ltlts_wmt32k   --t2t_usr_dir=/home/aleksas/workspace/stress/USR_DIR   --data_dir=/home/aleksas/workspace/stress/data
```
