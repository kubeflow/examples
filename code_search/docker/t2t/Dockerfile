ARG BASE_IMAGE_TAG=1.8.0

FROM tensorflow/tensorflow:$BASE_IMAGE_TAG

RUN pip --no-cache-dir install tensor2tensor~=1.8.0 oauth2client~=4.1.0 &&\
    apt-get update && apt-get install -y jq &&\
    rm -rf /var/lib/apt/lists/*


# These dependencies are primarily needed with Dataflow
# so we need to install them for Python2.
# We do this before copying the code because we don't want to have
# reinstall the requirements just because the code changed.
COPY src/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN pip install https://github.com/kubeflow/batch-predict/tarball/master

# install the spacy model
RUN python -m spacy download en

# The version of protobuf that ends up getting installed as the result
# of the above commands is too old (3.5); we end up getting errors
# when import apache_beam upgrading appears to fix this.
RUN pip install -U protobuf==3.6.1

ADD src/code_search /app/code_search
ADD src             /src

ADD docker/t2t/t2t-entrypoint.sh /usr/local/sbin/t2t-entrypoint

WORKDIR /app

ENV PYTHONIOENCODING=utf-8 T2T_USR_DIR=/app/code_search/t2t

VOLUME ["/data", "/output"]

ENTRYPOINT ["bash"]
