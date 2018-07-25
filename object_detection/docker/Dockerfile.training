FROM ubuntu:16.04

LABEL maintainer="Soila Kavulya <soila.p.kavulya@intel.com>"

# Pick up some TF dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libfreetype6-dev \
        libpng12-dev \
        libzmq3-dev \
        pkg-config \
        protobuf-compiler \
        python \
        python-dev \
        python-pil \
        python-tk \
        python-lxml \
        rsync \
        git \
        software-properties-common \
        unzip \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -O https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

RUN pip --no-cache-dir install \
        Cython \
        glob2 \
        h5py \
        ipykernel \
        jupyter \
        matplotlib \
        numpy \
        pandas \
        scipy \
        sklearn \
        six \
        tensorflow \
        tensorflow-serving-api \
        && \
    python -m ipykernel.kernelspec

# Setup Universal Object Detection
ENV MODELS_HOME "/models"
RUN git clone https://github.com/tensorflow/models.git $MODELS_HOME && cd $MODELS_HOME && git checkout r1.5
#COPY models $MODELS_HOME
RUN cd $MODELS_HOME/research \
        && protoc object_detection/protos/*.proto --python_out=.

ENV PYTHONPATH "$MODELS_HOME/research:$MODELS_HOME/research/slim:$PYTHONPATH"
COPY scripts /scripts
# TensorBoard
EXPOSE 6006

WORKDIR $MODELS_HOME

# Run training job
ARG pipeline_config_path
ARG train_dir

CMD ["python", "$MODELS_HOME/research/object_detection/train.py", "--logtostderr", "--pipeline_config_path=$pipeline_config_path"  "--train_dir=$train_dir"]
