
## Export the TensorFlow Graph  

Before exporting the graph we first need to identify a checkpoint candidate in the `pets-pvc` pvc under
`${MOUNT_PATH}/train` which is where the training job is saving the checkpoints.
  
To see what's being saved in `${MOUNT_PATH}/train` while the training job is running you can use:
```  
kubectl -n kubeflow exec -it pets-training-master-r1hv-0-i6k7c sh  
```  
This will open an interactive shell to your container and now you can execute `ls ${MOUNT_PATH}/train` and look for a
checkpoint candidate.  
  
Once you have identified the checkpoint next step is to configure the checkpoint in the `export-tf-graph-job` component and apply it.

```
CHECKPOINT="${TRAINING_DIR}/model.ckpt-<number>" #replace with your checkpoint number
INPUT_TYPE="image_tensor"
EXPORT_OUTPUT_DIR="${MOUNT_PATH}/exported_graphs"

ks param set export-tf-graph-job mountPath ${MOUNT_PATH}
ks param set export-tf-graph-job pvc ${PVC}
ks param set export-tf-graph-job image ${OBJ_DETECTION_IMAGE}
ks param set export-tf-graph-job pipelineConfigPath ${PIPELINE_CONFIG_PATH}
ks param set export-tf-graph-job trainedCheckpoint ${CHECKPOINT}
ks param set export-tf-graph-job outputDir ${EXPORT_OUTPUT_DIR}
ks param set export-tf-graph-job inputType ${INPUT_TYPE}

ks apply ${ENV} -c export-tf-graph-job
```  
To see the default values and params of the `export-tf-graph-job` component look at: [params.libsonnet](./ks-app/components/params.libsonnet)

Once the job is completed a new directory called `exported_graphs` under `/pets_data` in the pets-data-claim PCV  
will be created containing the model and the frozen graph.  

## Next
- Serve the model with  [CPU](./tf_serving_cpu.md) or [GPU](./tf_serving_gpu.md)
