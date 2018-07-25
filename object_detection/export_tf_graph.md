
## Export the TensorFlow Graph  

Before exporting the graph we first need to identify a checkpoint candidate in the `pets-pvc` pvc under
`/pets_data/train`.  
  
To see what's being saved in `/pets_data/train` while the training job is running you can use:
```  
kubectl -n kubeflow exec -it pets-training-master-r1hv-0-i6k7c sh  
```  
This will open an interactive shell to your container and now you can execute `ls /pets_data/train` and look for a  
checkpoint candidate.  
  
Once you have identified the checkpoint now we can generate the export-job component and apply it.
  
Generating the component:
```  
ks generate generic-job  export-tf-graph-job \
--pvc="pets-pvc" \
--mountPath="/pets_data" \
--image="lcastell/pets_object_detection" \
--command='["python", "models/research/object_detection/export_inference_graph.py"]' \
--args='["--input_type=image_tensor", \
"--pipeline_config_path=/pets_data/faster_rcnn_resnet101_pets.config", \
"--trained_checkpoint_prefix=/pets_data/train/model.ckpt-<number>", \
"--output_directory=/pets_data/exported_graphs"]'

ks apply ${ENV} -c export-tf-graph-job
```  
  
Once the job is completed a new directory called `exported_graphs` under `/pets_data` in the pets-data-claim PCV  
will be created containing the model and the frozen graph.  
  
Before serving the model we need to perform a quick hack since the object detection export python api does not  
generate a "version" folder for the saved model. This hack consists on creating a directory and move some files to it.  
One way of doing this is by accessing to an interactive shell in one of your running containers and moving the data yourself  
  
```  
kubectl -n kubeflow exec -it pets-training-master-r1hv-0-i6k7c sh  
mkdir /pets_data/exported_graphs/saved_model/1  
cp /pets_data/exported_graphs/saved_model/* /pets_data/exported_graphs/saved_model/1  
```  
  
## Serve the model using TF-Serving (CPU)

We will be using Kubeflow's tf-serving prototype to create our component, we will just need to edit a few things
in the yaml manifest after generating the component.

First create the component and configure some parameters:
```
MODEL_COMPONENT=pets-model
MODEL_NAME=pets-model
MODEL_PATH=/pets_data/exported_graphs/saved_model
MODEL_STORAGE_TYPE=nfs
NFS_PVC_NAME=nfs

ks generate tf-serving ${MODEL_COMPONENT} --name=${MODEL_NAME}
ks param set ${MODEL_COMPONENT} modelPath ${MODEL_PATH}
ks param set ${MODEL_COMPONENT} modelStorageType ${MODEL_STORAGE_TYPE}
ks param set ${MODEL_COMPONENT} nfsPVC ${NFS_PVC_NAME}
```

Now lets dump the contents of the pets-model component to a manifest yaml file:
```
ks show ${ENV} -c pets-model > pets-model-serving.yaml
```

Edit the pets-model-serving.yaml file to properly configure the volume mounts:
```
sed -i -e 's/mountPath: \/mnt/mountPath: \/pets_data/g' pets-model-serving.yaml
```

Apply the manifest file:
```
kubectl apply -f ./pets-model-serving.yaml
```

After that you should see pets-model pod. Run:
```
kubectl -n kubeflow get pods | grep pets-model
```  
That will output something like this:
```  
pets-model-v1-57674c8f76-4qrqp      1/1       Running     0          4h  
```  
Take a look at the logs:  
```  
kubectl -n kubeflow logs pets-model-v1-57674c8f76-4qrqp  
```  
And you should see:  
```  
2018-06-21 19:20:32.325406: I tensorflow_serving/core/loader_harness.cc:86] Successfully loaded servable version {name: pets-model version: 1}  
E0621 19:20:34.134165172       7 ev_epoll1_linux.c:1051]     grpc epoll fd: 3  
2018-06-21 19:20:34.135354: I tensorflow_serving/model_servers/main.cc:288] Running ModelServer at 0.0.0.0:9000 ...  
```
Now you can use a gRPC client to run inference using your trained model!
