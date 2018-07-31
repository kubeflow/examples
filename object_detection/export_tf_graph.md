
## Export the TensorFlow Graph  

Before exporting the graph we first need to identify a checkpoint candidate in the `pets-pvc` pvc under
`/pets_data/train`.  
  
To see what's being saved in `/pets_data/train` while the training job is running you can use:
```  
kubectl -n kubeflow exec -it pets-training-master-r1hv-0-i6k7c sh  
```  
This will open an interactive shell to your container and now you can execute `ls /pets_data/train` and look for a  
checkpoint candidate.  
  
Once you have identified the checkpoint now we can set the checkpoint in the `export-tf-graph-job` component and apply it.
To set the checkpoint we will need to update the args parameter of the `export-tf-graph-job` component.

```
# setting the args command. Change the --trained_checkpoint_prefix value.
# You can set more arguments if needed

ks param set export-tf-graph-job args \
'["--input_type=image_tensor","--pipeline_config_path=/pets_data/faster_rcnn_resnet101_pets.config","--trained_checkpoint_prefix=/pets_data/train/model.ckpt-<number>","--output_directory=/pets_data/exported_graphs"]'

ks apply ${ENV} -c export-tf-graph-job
```  
To see the default values and params of the `export-tf-graph-job` component look at: [params.libsonnet](./ks-app/components/params.libsonnet)

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
  
## Next
- Serve the model with  [CPU](./tf_serving_cpu) or [GPU](./tf_serving_gpu)
