#!/usr/bin/env bash

VERSION=$1
BUCKET=$2
DIR=/home/tensorflow/$VERSION

mkdir ${DIR}/output 

NGRAPH_TF_DUMP_CLUSTERS=1 NGRAPH_TF_DUMP_DECLUSTERED_GRAPHS=1 NGRAPH_TF_LOG_PLACEMENT=1 python /home/tensorflow/MNIST.py --version $VERSION --bucket $BUCKET
python get_node_encapsulate_map.py /home/tensorflow nodemap.pkl
python import_pb_to_tensorboard.py --model_dir ${DIR} --log_dir ${DIR}/output
#python ngtf_graph_viewer.py -c nodemap.pkl /home/tensorflow/saved_model.pbtxt $DIR
python ngtf_graph_viewer.py -c nodemap.pkl /home/tensorflow/mnist_model.pbtxt $DIR
/usr/local/bin/tensorboard --logdir=${DIR}
