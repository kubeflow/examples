## Monitor your job

### View status
```
kubectl -n kubeflow describe tfjobs pets-training
```

### View logs of individual pods
```
kubectl -n kubeflow get pods
kubectl -n kubeflow logs <name_of_pod>
```
**NOTE:** When the job finishes, the pods will be automatically terminated. In order to see terminated pods run the `get pods` command with the `-a` flag:
```
kubectl -n kubeflow get pods -a
```

When the job finishes you will be seeing something like this in your completed/terminated pods logs:
```
INFO:tensorflow:Starting Session.
INFO:tensorflow:Saving checkpoint to path /tmp/pets/train/model.ckpt
INFO:tensorflow:Starting Queues.
INFO:tensorflow:global_step/sec: 0
INFO:tensorflow:Recording summary at step 200006.
INFO:tensorflow:global step 200006: loss = 0.0091 (9.854 sec/step)
INFO:tensorflow:Stopping Training.
INFO:tensorflow:Finished training! Saving model to disk.
```

Now you have a trained model!! find it at `/tmp/pets/train` directory in all of your cluster nodes.

### Delete job
```
kubectl -n kubeflow delete -f training/pets-tf-jobs.yaml
```

## Next
[Serving your trained model with TF-serving]()