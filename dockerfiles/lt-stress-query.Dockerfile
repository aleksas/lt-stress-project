FROM tensorflow/tensorflow:1.15.3

ARG MODEL_SERVER_ADDRESS=172.17.0.1:8500
# USE "/sbin/ip route|awk '/default/ { print $3 }'" to determine host ip address
# 172.17.0.1 - default ?

ENV MODEL_NAME=stress-transformer-lite-v1
ENV PROBLEM_NAME=translate_ltlts_wmt32k

ENV DATA_DIR=/data/${MODEL_NAME}
ENV PROBLEM_DIR=/problems/${PROBLEM_NAME}
# PREPARE UTILITIES

RUN apt update
RUN apt -y install wget

#RUN pip install oauth2client requests tf_slim scipy sympy tqdm gym pillow pypng google-api-python-client
#RUN pip install tensorflow-serving-api==1.15.0 tensorflow_probability==0.7.0 tensorflow-datasets==3.0.0
#RUN pip install tensor2tensor==1.15.0 --no-deps

ADD requirements.txt /root
RUN pip install -r /root/requirements.txt

# DOWNLOAD PROBLEM

RUN mkdir -p ${PROBLEM_DIR}
WORKDIR ${PROBLEM_DIR}

RUN wget https://github.com/aleksas/lt-stress-project/releases/download/0.0.2/translate_ltlts.py
RUN wget https://github.com/aleksas/lt-stress-project/releases/download/0.0.2/__init__.py

# DOWNLOAD SUBWORD DICT

RUN mkdir -p ${DATA_DIR}
WORKDIR ${DATA_DIR}

RUN wget https://github.com/aleksas/lt-stress-project/releases/download/0.0.2/vocab.translate_ltlts_wmt32k.32768.subwords

WORKDIR /root
RUN echo "t2t-query-server  \
    --server=${MODEL_SERVER_ADDRESS} \
    --servable_name=${MODEL_NAME} \
    --problem=${PROBLEM_NAME} \
    --t2t_usr_dir=${PROBLEM_DIR} \
    --data_dir=${DATA_DIR}" > run.sh

RUN pip install flask

RUN mkdir -p /root/app
ADD index.html /root/app
ADD app.py /root/app
WORKDIR /root/app
ENTRYPOINT [ "flask", "run" ]