FROM tensorflow/tensorflow:1.15.3

ARG MODEL_SERVER_ADDRESS=172.17.0.1:8500
# USE "/sbin/ip route|awk '/default/ { print $3 }'" to determine host ip address
# 172.17.0.1 - default ?

ENV MODEL_NAME=stress-transformer-lite-v1
ENV PROBLEM_NAME=translate_ltlts_wmt32k

ENV DATA_DIR=/data/${MODEL_NAME}
ENV PROBLEM_DIR=/problems/${PROBLEM_NAME}

# INSTALL BASE

RUN apt update
RUN apt -y install wget

# DOWNLOAD PROBLEM

RUN mkdir -p ${PROBLEM_DIR}
WORKDIR ${PROBLEM_DIR}

RUN wget https://github.com/aleksas/lt-stress-project/releases/download/0.0.2/translate_ltlts.py
RUN wget https://github.com/aleksas/lt-stress-project/releases/download/0.0.2/__init__.py

# DOWNLOAD SUBWORD DICT

RUN mkdir -p ${DATA_DIR}
WORKDIR ${DATA_DIR}

RUN wget https://github.com/aleksas/lt-stress-project/releases/download/0.0.2/vocab.translate_ltlts_wmt32k.32768.subwords

# INSIGHTS

RUN apt -y install nodejs npm git fakeroot
RUN npm install -g bower
WORKDIR /root
RUN git clone https://github.com/tensorflow/tensor2tensor.git
WORKDIR /root/tensor2tensor/tensor2tensor/insights/polymer
RUN git checkout tags/v1.15.6
RUN bower install --allow-root

# PREPARE UTILITIES

ADD requirements.txt /root
RUN pip install -r /root/requirements.txt

# PPEPARE RUN SCRIPT

WORKDIR /root
RUN echo "t2t-insights-server  \
    --configuration=configuration.json \
    --t2t_usr_dir=${PROBLEM_DIR} \
    --static_path=/root/tensor2tensor/insights/polymer" > run.sh

RUN pip install flask gunicorn==19.9.0
RUN pip install mesh-tensorflow tensorflow_gan --use-feature=2020-resolver

ADD configuration.json /root/

#ENTRYPOINT [ "/bin/bash", "/root/run.sh" ]