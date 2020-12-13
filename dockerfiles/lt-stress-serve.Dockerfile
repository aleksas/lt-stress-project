FROM tensorflow/serving:2.3.0

ENV MODEL_NAME=stress-transformer-lite-v1
ENV PROBLEM_NAME=translate_ltlts_wmt32k

# PREPARE UTILITIES

RUN apt update
RUN apt -y install wget unzip

# DOWNLOAD EXPORTED MODEL

RUN mkdir -p /models/${MODEL_NAME}
WORKDIR /models/${MODEL_NAME}

RUN wget https://github.com/aleksas/lt-stress-project/releases/download/0.0.2/1607278770-20201206T182228Z-001.zip
RUN unzip 1607278770-20201206T182228Z-001.zip
RUN rm 1607278770-20201206T182228Z-001.zip

# DOWNLOAD PROBLEM

RUN mkdir -p /problems/${PROBLEM_NAME}
WORKDIR /problems/${PROBLEM_NAME}

RUN wget https://github.com/aleksas/lt-stress-project/releases/download/0.0.2/translate_ltlts.py
RUN wget https://github.com/aleksas/lt-stress-project/releases/download/0.0.2/__init__.py

# REST
EXPOSE 8501 
# gRPC
EXPOSE 8500

ENTRYPOINT ["/usr/bin/tf_serving_entrypoint.sh"]
