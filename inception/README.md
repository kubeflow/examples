# Inception V3 Example
---
### Download the checkpoint from [tensorflow/models](https://github.com/tensorflow/models/tree/master/research/slim)

Using the script `./download_v3_checkpoint.sh`

### Install Dependencies

`pip install -r requirements.txt`

### Export the model

`
MODEL_PATH=gs://kubeflow-models/inception
python export_inception_v3.py --output_dir=${MODEL_PATH} --model_version=2`

### Deploy with GRPC or REST API using kubeflow

```
ks init my-model-server
cd my-model-server
ks registry add kubeflow github.com/kubeflow/kubeflow/tree/master/kubeflow
ks pkg install kubeflow/tf-serving
ks env add  cloud
MODEL_COMPONENT=serveInception
MODEL_NAME=inception
#Replace this with the url to your bucket if using your own model
MODEL_PATH=gs://kubeflow-models/inception
MODEL_SERVER_IMAGE=gcr.io/$(gcloud config get-value project)/model-server:1.0
# if you need REST API need to provide http_proxy_image
HTTP_PROXY_IMAGE=gcr.io/$(gcloud config get-value project)/http-proxy:1.0
ks generate tf-serving ${MODEL_COMPONENT} --name=${MODEL_NAME} --namespace=default --model_path=${MODEL_PATH} --model_server_image=${MODEL_SERVER_IMAGE} --http_proxy_image=${HTTP_PROXY_IMAGE}

ks apply cloud -c ${MODEL_COMPONENT}

```


### Use model with REST API
Find the ip address and port by
```
kubectl get services
NAME         TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)			 AGE
$MODEL_NAME  LoadBalancer   <INTERNAL IP>   <SERVICE IP>     <SERVICE PORT>:<NODE PORT>,<HTTP SERVICE PORT>:<NODE PORT>  <TIME SINCE DEPLOYMENT>

```

Query the result by

```
(echo '{"instances": [{"image_contents": {"b64": "'; base64 ./inception-client/images/sleeping-pepper.jpg; echo '"}}]}') | curl -H "Content-Type: application/json" -X POST -d @-  <SERVICE IP>:<HTTP SERVICE PORT>/model/image_classification:predict
```

And get Prediction

```
{"predictions":
	[
		{
		  "labels": "Border terrier",
		  "probs": 0.12965676188468933
		},
		{
		  "labels": "bull mastiff",
		  "probs": 0.10835129022598267
		},
		{
		  "labels": "malinois",
		  "probs": 0.10788080841302872
		},
		{
		  "labels": "boxer",
		  "probs": 0.03579695522785187
		},
		{
		  "labels": "French bulldog",
		  "probs": 0.02937905490398407
		}
	  ]
}
```
