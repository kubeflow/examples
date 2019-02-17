{"apiVersion":"kubeflow.org/v1alpha2","kind":"PyTorchJob","metadata":{"name":"pytorch-mnist-ddp-gpu"},"spec":{"pytorchReplicaSpecs":{"Master":{"replicas":1,"restartPolicy":"OnFailure","template":{"spec":{"containers":[{"image":"gcr.io/kubeflow-examples/pytorch-mnist/traingpu","name":"pytorch","resources":{"limits":{"nvidia.com/gpu":1}},"volumeMounts":[{"mountPath":"/mnt/kubeflow-gcfs","name":"kubeflow-gcfs"}]}],"volumes":[{"name":"kubeflow-gcfs","persistentVolumeClaim":{"claimName":"kubeflow-gcfs","readOnly":false}}]}}},"Worker":{"replicas":3,"restartPolicy":"OnFailure","template":{"spec":{"containers":[{"image":"gcr.io/kubeflow-examples/pytorch-mnist/traingpu","name":"pytorch","resources":{"limits":{"nvidia.com/gpu":1}},"volumeMounts":[{"mountPath":"/mnt/kubeflow-gcfs","name":"kubeflow-gcfs"}]}],"volumes":[{"name":"kubeflow-gcfs","persistentVolumeClaim":{"claimName":"kubeflow-gcfs","readOnly":false}}]}}}}}}
