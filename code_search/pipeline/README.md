To run the pipeline, follow the kubeflow pipeline instruction and compile index_update_pipeline.py and upload to pipeline
page.

Provide the parameter, e.g. 

```
PROJECT='code-search-demo'
CLUSTER_NAME='cs-demo-1103'
WORKING_DIR='gs://code-search-demo/pipeline'
SAVED_MODEL_DIR='gs://code-search-demo/models/20181107-dist-sync-gpu/export/1541712907/'
DATA_DIR='gs://code-search-demo/20181104/data'
```