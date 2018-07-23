
## Export the TensorFlow Graph  

Before exporting the graph we first need to identify a checkpoint candidate in the `pets-data-claim` pvc under
`/pets_data/train`.  
  
To see what's being saved in `/pets_data/train` while the training job is running you can use:
```  
kubectl -n kubeflow exec -it pets-training-master-r1hv-0-i6k7c sh  
```  
This will open an interactive shell to your container and now you can execute `ls /pets_data/train` and look for a  
checkpoint candidate.  
  
Once you have identified the checkpoint now we can generate the export-job component and apply it
  
Generating the component:
```  
ks generate generic-job  export-tf-graph-job \
--pvc="pets-pvc" \
--mountPath="/pets-data" \
--image="lcastell/pets_object_detection" \
--command=["python", "models/research/object_detection/export_inference_graph.py"] \
--args=["--input_type=image_tensor", \
"--pipeline_config_path=/pets_data/faster_rcnn_resnet101_pets.config", \
"--trained_checkpoint_prefix=/pets_data/train/model.ckpt-<number>", \
"--output_directory=/pets_data/exported_graphs"]

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
