ARG BASE_IMAGE_TAG=1.8.0

FROM tensorflow/tensorflow:$BASE_IMAGE_TAG

RUN pip --no-cache-dir install tensor2tensor~=1.7.0 oauth2client~=4.1.0 &&\
    apt-get update && apt-get install -y jq &&\
    rm -rf /var/lib/apt/lists/*

ADD src/code_search/t2t /app/code_search/t2t
ADD docker/t2t/t2t-entrypoint.sh /usr/local/sbin/t2t-entrypoint

WORKDIR /app

ENV PYTHONIOENCODING=utf-8 T2T_USR_DIR=/app/code_search/t2t

VOLUME ["/data", "/output"]

ENTRYPOINT ["bash"]
