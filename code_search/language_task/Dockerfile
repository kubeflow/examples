# NOTE: The context for this build must be the `language_task` directory

ARG BASE_IMAGE_TAG=1.8.0-py3

FROM tensorflow/tensorflow:$BASE_IMAGE_TAG

ADD requirements.txt /

RUN pip3 --no-cache-dir install -r /requirements.txt &&\
    apt-get update && apt-get install -y jq &&\
    rm -rf /var/lib/apt/lists/*

VOLUME ["/data", "/output"]

ADD t2t_problems/* /t2t_problems/
ADD t2t-entrypoint.sh /usr/local/sbin/t2t-entrypoint

ENV T2T_USR_DIR=/t2t_problems

WORKDIR /t2t_problems

#ENTRYPOINT ["/usr/local/sbin/t2t-entrypoint"]

# TODO(sanyamkapoor): A workaround for tensorflow/tensor2tensor#879
RUN apt-get update && apt-get install -y curl python &&\
    curl https://sdk.cloud.google.com | bash &&\
    rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["bash"]
