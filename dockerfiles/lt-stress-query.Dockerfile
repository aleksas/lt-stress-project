FROM tensorflow/tensorflow:1.15.3

ARG MODEL_SERVER_ADDRESS=172.17.0.1:8500
ENV MODEL_SERVER_ADDRESS=$MODEL_SERVER_ADDRESS
# USE "/sbin/ip route|awk '/default/ { print $3 }'" to determine host ip address
# 172.17.0.1 - default ?

ENV MODEL_NAME=stress-transformer-lite-v1
ENV PROBLEM_NAME=translate_ltlts_wmt32k

ENV DATA_DIR=/data/${MODEL_NAME}
ENV PROBLEM_DIR=/problems/${PROBLEM_NAME}
# PREPARE UTILITIES

RUN apt update
RUN apt -y install wget

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
RUN pip install flask

RUN mkdir -p /root/app
ADD index.html /root/app
ADD app.py /root/app
WORKDIR /root/app
ENTRYPOINT [ "flask", "run", "--host", "0.0.0.0" ]