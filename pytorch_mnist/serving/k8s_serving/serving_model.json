{
  "apiVersion": "machinelearning.seldon.io/v1alpha2",
  "kind": "SeldonDeployment",
  "metadata": {
    "labels": {
      "app": "seldon"
    },
    "name": "mnist-classifier"
  },
  "spec": {
    "annotations": {
      "deployment_version": "v1",
      "project_name": "MNIST Example"
    },
    "name": "mnist-classifier",
    "predictors": [
      {
        "annotations": {
          "predictor_version": "v1"
        },
        "componentSpecs": [{
          "spec": {
            "containers": [
              {
                "image": "gcr.io/kubeflow-examples/mnistddpserving",
                "imagePullPolicy": "Always",
                "name": "pytorch-model",
                "volumeMounts": [
                  {
                    "mountPath": "/mnt/kubeflow-gcfs",
                    "name": "persistent-storage"
                  }
                ]
              }
            ],
            "terminationGracePeriodSeconds": 1,
            "volumes": [
              {
                "name": "persistent-storage",
                "volumeSource" : {
                  "persistentVolumeClaim": {
                    "claimName": "kubeflow-gcfs"
                  }
                }
              }
            ]
          }
        }],
        "graph": {
          "children": [],
          "endpoint": {
            "type": "GRPC"
          },
          "name": "pytorch-model",
          "type": "MODEL"
        },
        "name": "mnist-ddp-serving",
        "replicas": 1
      }
    ]
  }
}