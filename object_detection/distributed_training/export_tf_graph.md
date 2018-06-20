## Export the TensorFlow Graph

In the [jobs](./jobs) directory you will find a manifest file [export-tf-graph.yaml](export-tf-graph.yaml).
Before executing the job we first need to identify a checkpoint candidate in the `pets-data-claim` pvc under
`/pets_data`.

Once you have identified the checkpoint open the `export-tf-graph.yaml` file and edit the container
command args: `--trained_checkpoint_prefix model.ckpt-<number>` (line 20) to match the chosen checkpoint.

Now we can execute the job with:
```
kubectl -n kubeflow apply ./jobs/export-tf-graph.yaml
```

Once the job is completed a new directory called `exported_graphs` under `/pets_data` in the pets-data-claim PCV
will be created containing the model and the frozen graph

## Serve the model using TF-Serving

Apply the manifest file under [tf-serving](./tf-serving) directory:
```
kubectl -n kubeflow apply -f tf-serving.yaml
```
