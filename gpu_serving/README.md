# Serving an object detection model with GPU

Reference
[blog](https://cloud.google.com/blog/big-data/2017/09/performing-prediction-with-tensorflow-object-detection-models-on-google-cloud-machine-learning-engine)

## Deploy Kubeflow
First, follow getting started
[guide](https://www.kubeflow.org/docs/started/getting-started/) to deploy
kubeflow.

## Prepare model
Download the model from model zoo.
The model should be in SavedModel format (including a `saved_model.pb` file and a
optional `variables/` folder.

```
wget http://download.tensorflow.org/models/object_detection/faster_rcnn_nas_coco_2018_01_28.tar.gz
tar -xzf faster_rcnn_nas_coco_2018_01_28.tar.gz
gsutil cp faster_rcnn_nas_coco_2018_01_28/saved_model/saved_model.pb gs://YOUR_BUCKET/YOUR_MODEL/1/
```

## Deploy serving component

```
ks init ks-app
cd ks-app
ks registry add kubeflow github.com/kubeflow/kubeflow/tree/master/kubeflow
ks pkg install kubeflow/tf-serving

ENV=YOUR_ENV
ks env add $ENV
ks env set $ENV --namespace kubeflow

ks generate tf-serving model1 --name=coco
ks param set model1 modelPath gs://YOUR_BUCKET/YOUR_MODEL/
ks param set model1 numGpus 1
ks apply $ENV -c model1
```

## Send prediction
```
python predict.py --url=YOUR_KF_HOST/models/coco
```

The script takes an input image (by default image1.jpg) and should save the result as `output.jpg`.
The output image has the bounding boxes for detected objects.
