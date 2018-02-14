# Inception V3 Example
---
### Download the checkpoint from [tensorflow/models](https://github.com/tensorflow/models/tree/master/research/slim)

Using the script `./download_v3_checkpoint.sh`

### Install Dependencies

`pip install -r requirements.txt`

### Export the model

`python export_inception_v3.py --output_dir=gs://kubeflow/inception --model_version=2`

### Deploy with GRPC or REST API using kubeflow

Pending https://github.com/kubeflow/kubeflow/pull/228
