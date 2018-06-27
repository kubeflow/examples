

Deploy Kubeflow


```
wget http://download.tensorflow.org/models/object_detection/faster_rcnn_nas_coco_2018_01_28.tar.gz
tar -xzf faster_rcnn_nas_coco_2018_01_28.tar.gz
gsutil cp faster_rcnn_nas_coco_2018_01_28/saved_model/saved_model.pb gs://YOUR_BUCKET/XXX/1/

ks init ks-app
cd ks-app
ks registry add X
ks pkg install X

ENV=YOUR_ENV
ks env add $ENV
ks env set $ENV --namespace kubeflow

ks generate tf-serving model1 --name=coco
ks param set model1 modelPath
ks param set model1 numGpus 1
ks apply $ENV -c model1
```

