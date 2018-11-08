# Demo

This directory contains assets for setting up a demo of the code search example.
It is primarily intended for use by Kubeflow contributors working on the shared demo.

Users looking to run the example should follow the README.md in the parent directory.

# GCP Resources

We are using the following project

* **org**: kubeflow.org
* **project**: code-search-demo
* **[code-search-team@kubeflow.org](https://github.com/kubeflow/internal-acls/blob/master/code-search-team.members.txt)** Google group administering access

# Results

## 2018-11-05

jlewi@ ran experiments that produced the following results

| What | location | Description
|------|----------|-------------------------
| Preprocessed data|  gs://code-search-demo/20181104/data/func-doc-pairs-00???-of-00100.csv |  This is the output of the Dataflow preprocessing job
| Training data | gs://code-search-demo/20181104/data/kf_github_function_docstring-train-00???-of-00100 | TFRecord files produced by running T2T datagen


### Models

| hparams | Location 
|---------| -------- 
| transformer_tine | gs://code-search-demo/models/20181105-tinyparams/
| transformer_base_single_gpu | gs://code-search-demo/models/20181105-single-gpu
| transformer_base | gs://code-search-demo/models/20181107-dist-sync-gpu

## Performance

| hparams | Resources | Steps/sec
|----------|----------|---------------------
| transformer_tiny | 1 CPU worker|  ~1.8 global step /sec
| transformer_base_single_gpu | 1 GPU worker (K80) | ~3.22611 global step /sec
| transformer_base | 1 chief with K80, 8 workers with 1 K80, sync training| ~ 0.0588723 global step /sec
| transformer_base | 1 chief (no GPU), 8 workers (no GPU), sync training| ~ 0.707014 global step /sec









