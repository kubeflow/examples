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
**NOTE:** When the job finishes, the pods will be automatically terminated. To see, run the `get pods` command with the `-a` flag:
```
kubectl -n kubeflow get pods -a
```

While the job is running, you should see something like this in your master pod logs:
```
INFO:tensorflow:Saving checkpoint to path /pets_data/train/model.ckpt
INFO:tensorflow:Recording summary at step 819.
INFO:tensorflow:global step 819: loss = 0.8603 (19.898 sec/step)
INFO:tensorflow:global step 822: loss = 1.9421 (18.507 sec/step)
INFO:tensorflow:global step 825: loss = 0.7147 (17.088 sec/step)
INFO:tensorflow:global step 828: loss = 1.7722 (18.033 sec/step)
INFO:tensorflow:global step 831: loss = 1.3933 (17.739 sec/step)
INFO:tensorflow:global step 834: loss = 0.2307 (16.493 sec/step)
INFO:tensorflow:Recording summary at step 839
```

When the job finishes, you should see something like this in your completed/terminated pods logs:
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
[Export the Tesorflow Graph]()