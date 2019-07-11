# Monitor your training job

The training component contains a TensorBoard visualization (TensorBoard viewer), which makes is comfortable to open the TensorBoard session for training jobs.

The logs of the training are uploaded to a Google Cloud Storage Bucket. TensorBoard automatically references this log location and displays the corresponding data. 

## Open TensorBoard
To open TensorBoard click on the `training` component in your experiment run. Located on the ride side is the artifact windows which shows a very handy button called (Open TensorBoard).

## How is this visualization component implemented?

In order to use his visualizations, your pipeline component must write a JSON file. Kubeflow provides a good documenation on [how visualizations are working](https://www.kubeflow.org/docs/pipelines/sdk/output-viewer/) and what types are available.

```
# write out TensorBoard viewer
metadata = {
    'outputs' : [{
      'type': 'tensorboard',
      'source': args.input_job_dir,
    }]
}

with open('/mlpipeline-ui-metadata.json', 'w') as f:
  json.dump(metadata, f)
```

*Next*: [Predict](step-7-predictions.md)

*Previous*: [Run the pipeline](step-5-run-pipeline.md)