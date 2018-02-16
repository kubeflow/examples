# Container builder

[![Docker Repository on Quay](https://quay.io/repository/cwbeitel/builder/status "Docker Repository on Quay")](https://quay.io/repository/cwbeitel/builder)

A custom container builder image can be built in the standard way, e.g.

```bash
YOUR_BUILDER_IMAGE_TAG=quay.io/someuser/builder:0.1

docker build -t $TAG .

gcloud docker -- push $TAG
```

Then specified in the [container builder workflow](../config/builder.yaml) as an argument as follows:

```bash
argo submit config/builder.yaml --namespace kubeflow \
    --parameter builder-image=${YOUR_BUILDER_IMAGE_TAG}
    ...
```

Please refer to the [demonstration notebook](../demo/demo.ipynb) for more details.
