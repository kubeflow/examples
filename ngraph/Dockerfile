FROM tensorflow/tensorflow:1.12.0

RUN apt-get update && apt-get install -y vim

# add google cloud storage
RUN pip --no-cache-dir install \
        google-cloud-storage \
        && \
    python -m ipykernel.kernelspec

RUN  pip install -U ngraph-tensorflow-bridge && \
python -c "import tensorflow as tf; print('TensorFlow version: r',tf.__version__);import ngraph_bridge; print(ngraph_bridge.__version__)"

RUN mkdir /home/tensorflow

# show python logs as they occur
ENV PYTHONUNBUFFERED=0

# include version as argument to docker build
ARG version=1
ENV VERSION=$version

# run MNIST.py with included arguments
ADD MNIST.py /home/tensorflow
ADD MNIST.sh /home/tensorflow
ADD get_node_encapsulate_map.py /home/tensorflow
ADD import_pb_to_tensorboard.py /home/tensorflow
ADD ngtf_graph_viewer.py /home/tensorflow
WORKDIR /home/tensorflow
ENTRYPOINT ./MNIST.sh $VERSION
