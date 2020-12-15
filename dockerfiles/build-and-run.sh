docker build -t aleksas/lt-stress-serve:0.0.2 -f lt-stress-serve.Dockerfile .
docker build -t aleksas/lt-stress-query:0.0.2 -f lt-stress-query.Dockerfile .

docker run -p 8050:8050 -p 8051:8051 aleksas/lt-stress-serve:0.0.2  /dev/null 2>&1 &
docker run -ti aleksas/lt-stress-query:0.0.2 bash

