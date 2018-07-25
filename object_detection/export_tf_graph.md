
## Export the TensorFlow Graph  
  
In the [jobs](./jobs) directory you will find a manifest file [export-tf-graph.yaml](./jobs/export-tf-graph.yaml).
Before executing the job we first need to identify a checkpoint candidate in the `pets-data-claim` pvc under  
`/pets_data/train`.  
  
To see what's being saved in `/pets_data/train` while the training job is running you can use:
```  
kubectl -n kubeflow exec -it pets-training-master-r1hv-0-i6k7c sh  
```  
This will open an interactive shell to your container and now you can execute `ls /pets_data/train` and look for a  
checkpoint candidate.  
  
Once you have identified the checkpoint open the `export-tf-graph.yaml` file under the ./jobs directory  
and edit the container command args: `--trained_checkpoint_prefix model.ckpt-<number>`  
(line 20) to match the chosen checkpoint.  
  
Now you can execute the job with:  
```  
kubectl -n kubeflow apply ./jobs/export-tf-graph.yaml  
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
