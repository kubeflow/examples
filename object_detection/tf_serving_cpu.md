## Serve the model using TF-Serving (CPU)

We will be using Kubeflow's tf-serving prototype to create our component, we will just need to edit a few things
in the yaml manifest after generating the component.

First create the component and configure some parameters:
```
MODEL_COMPONENT=pets-model
MODEL_NAME=pets-model
MODEL_PATH=/pets_data/exported_graphs/saved_model
MODEL_STORAGE_TYPE=nfs
NFS_PVC_NAME=pets-pvc

ks generate tf-serving ${MODEL_COMPONENT} --name=${MODEL_NAME}
ks param set ${MODEL_COMPONENT} modelPath ${MODEL_PATH}
ks param set ${MODEL_COMPONENT} modelStorageType ${MODEL_STORAGE_TYPE}
ks param set ${MODEL_COMPONENT} nfsPVC ${NFS_PVC_NAME}
```

Now lets dump the contents of the pets-model component to a manifest yaml file:
```
ks show ${ENV} -c pets-model > pets-model-serving.yaml
```

Edit the pets-model-serving.yaml file to properly configure the volume mounts:
```
sed -i -e 's/mountPath: \/mnt/mountPath: \/pets_data/g' pets-model-serving.yaml
```

Apply the manifest file:
```
kubectl apply -f ./pets-model-serving.yaml
```

After that you should see pets-model pod. Run:
```
kubectl -n kubeflow get pods | grep pets-model
```
That will output something like this:
```
pets-model-v1-57674c8f76-4qrqp      1/1       Running     0          4h
```
Take a look at the logs:
```
kubectl -n kubeflow logs pets-model-v1-57674c8f76-4qrqp
```
And you should see:
```
2018-06-21 19:20:32.325406: I tensorflow_serving/core/loader_harness.cc:86] Successfully loaded servable version {name: pets-model version: 1}
E0621 19:20:34.134165172       7 ev_epoll1_linux.c:1051]     grpc epoll fd: 3
2018-06-21 19:20:34.135354: I tensorflow_serving/model_servers/main.cc:288] Running ModelServer at 0.0.0.0:9000 ...
```
Now you can use a gRPC client to run inference using your trained model!