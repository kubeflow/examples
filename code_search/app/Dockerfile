# NOTE: The context for this build must be the `app` directory

ARG BASE_IMAGE_TAG=1.8.0-py3

FROM tensorflow/tensorflow:$BASE_IMAGE_TAG

ADD . /app

WORKDIR /app

ENV T2T_USR_DIR=/app/code_search/t2t

RUN pip3 --no-cache-dir install . &&\
    apt-get update && apt-get install -y jq &&\
    rm -rf /var/lib/apt/lists/* &&\
    ln -s /app/t2t-entrypoint.sh /usr/local/sbin/t2t-entrypoint

# TODO(sanyamkapoor): A workaround for tensorflow/tensor2tensor#879
RUN apt-get update && apt-get install -y curl python &&\
    curl https://sdk.cloud.google.com | bash &&\
    rm -rf /var/lib/apt/lists/*

VOLUME ["/data", "/output"]

EXPOSE 8008

ENTRYPOINT ["bash"]
