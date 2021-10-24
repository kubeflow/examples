# Distributed training
In this part, we will implement distributed training in KubeFlow Pipeline. The method used is Tensorflow's MultiWorkerMirroredStrategy CPU. In this tutorial, we will learn how to specify pods to be deployed under a specific node, and how to communicate with each worker.

## Before training
Before running the training program, we need to make some settings, include:

* Adding tags to each node.
* Deploying service YAML file.
* Add label name to your pod on the pipeline.
* Use add_node_selector_constraint to specify pod deployed under a specific node
* Add TF_config environment variables to the code.

### Adding tags to each node 
The purpose of adding tags is that the subsequent steps can directly specify the pod to be deployed under a specific node.
You run following commands to apply your node. The added screen example can shown in the **Figure.1** .
```commandline
  // add tags
  kubectl label nodes <node name>  <label name> = <value>  
  
  //show your node information
  kubectl get nodes  --show-labels=true 
```
<div align=center><img width="1000" height="100" src="https://user-images.githubusercontent.com/51089749/137849536-0bd6ad8f-f143-4eb2-8ad4-643f42cb225b.png"/></div>
<p align ="center"> <b>Figure1. Example added tags.</b></p>

### Deploying service YAML file
When performing distributed training, worker and other workers must use the network to communicate with each other, so the pod's external port must be opened and connected to the outside through the service.
We have a [service YAML](https://github.com/mike0355/k8s-facenet-distributed-training/tree/main/pod-service) file that provides service, so you don’t need to rewrite a new file for deployment, as shown in **Figure.2** .

<div align=center><img width="500" height="500" src="https://user-images.githubusercontent.com/51089749/137850906-49510b51-9343-4d5b-83d8-d249833fcccc.png"/></div>
<p align ="center"> <b>Figure2. Example of service yaml format.</b></p>

You can run following the commands to deploy and check your service YAML file, as shown in **Figure.3**
```commandline
  //Deploy your service.yaml
  kubectl create -f <your service YAML file name>
  
  //check your service.
  kubectl get svc -n kubeflow-user-example-com
```
<div align=center><img width="1000" height="50" src="https://user-images.githubusercontent.com/51089749/137852149-fc1f2273-c39e-4739-ad33-25e20cb8bd66.png"/></div>
<p align ="center"> <b>Figure3. Example of check service.</b></p>

### Add label name to your pod on the pipeline
The purpose of adding the label name is that the Service file we deployed earlier can rely on the label name to open a port to a specific pod. We found the method to add the label name to a pod on the pipeline from the website of the [KubeFlow Pipeline SDK](https://kubeflow-pipelines.readthedocs.io/en/stable/source/kfp.dsl.html), as shown in **Figure.4** .

<div align=center><img width="500" height="200" src="https://user-images.githubusercontent.com/51089749/137856365-c92e4e5e-29c8-4402-a83b-4b1e3cc5c767.png"/></div>
<p align ="center"> <b>Figure4. Example added label name command.</b></p>

However, the actual way to add to the pipeline is as shown in the **Figure.5** , we need to define the name and value on the KubeFlow pipeline. Please make sure your name and value is the same as your selector parameter in your service YAML file.

<div align=center><img width="500" height="150" src="https://user-images.githubusercontent.com/51089749/137860311-7334525b-9683-4965-81a2-f1c3e09f048c.png"/></div>
<p align ="center"> <b>Figure5. Example of define label on pipeline.</b></p>

### Use add_node_selector_constraint to specify pod deployed under a specific node
Using this command, the pod on the pipeline can be designated to be deployed and executed under a specific node. We found the method to add the label name to a pod on the pipeline from the website of the [KubeFlow Pipeline SDK](https://kubeflow-pipelines.readthedocs.io/en/stable/source/kfp.dsl.html), as shown in **Figure.7** .

<div align=center><img width="400" height="150" src="https://user-images.githubusercontent.com/51089749/137860986-5122936c-c63a-4caf-ba0b-7ac2509846af.png"/></div>
<p align ="center"> <b>Figure7. Example of add node selector.</b></p>

On the pipeline, we need to define name and value at the first, as shown in **Figure.8**, please make sure your name and value is the same as your Kubernetes node's tag. 
<div align=center><img width="400" height="150" src="https://user-images.githubusercontent.com/51089749/137861803-df3c25fa-e6f9-4234-9446-d685cba00639.png"/></div>
<p align ="center"> <b>Figure8. Example of add node selector on pipeline.</b></p>

After define label name and node selector, you can use Kubeflow SDK in your pod.
```commandline
     //worker1
    distributed_training_worker1_task=distributed_training_worker1_op(load_data_task.outputs['start_time_string']).add_pvolumes({ 
       log_folder:vop.volume,
    }).add_pod_label(name,value1).add_node_selector_constraint(label_name,label_value1).add_port(V1ContainerPort(container_port=3000,host_port=3000))
        
     //worker2
    distributed_training_worker2_task=distributed_training_worker2_op(load_data_task.outputs['start_time_string']).add_pvolumes({ 
        log_folder:vop.volume,
    }).add_pod_label(name,value2).add_port(V1ContainerPort(container_port=3000,host_port=3000)).add_node_selector_constraint(label_name,label_value2)
    
    //worker3
    distributed_training_worker3_task=distributed_training_worker3_op(load_data_task.outputs['start_time_string']).add_pvolumes({ 
        log_folder:vop.volume,
    }).add_pod_label(name,value3).add_port(V1ContainerPort(container_port=3000,host_port=3000)).add_node_selector_constraint(label_name,label_value3)
```
### Add TF_config environment variables to the code.
This tutorial use the Tensorflow's MultiWorkerMirroredStrategy to implement distributedtraining, so we need to apply the environment variable of TF_config in each pod. We use os.environ to export the TF_config in environment variable.
```commandline
    //worker1
        os.environ['TF_CONFIG'] = json.dumps({'cluster': {'worker': ["pipeline-worker-1:3000","pipeline-worker-2:3000","pipeline-worker-3:3000"]},'task': {'type': 'worker', 'index': 0}})
    
    //worker2
        os.environ['TF_CONFIG'] = json.dumps({'cluster': {'worker': ["pipeline-worker-1:3000","pipeline-worker-2:3000","pipeline-worker-3:3000"]},'task': {'type': 'worker', 'index': 1}})
    
    //worker3
        os.environ['TF_CONFIG'] = json.dumps({'cluster': {'worker': ["pipeline-worker-1:3000","pipeline-worker-2:3000","pipeline-worker-3:3000"]},'task': {'type': 'worker', 'index': 2}})
```

# Pipeline
After the previous settings, the pipeline we built is as shown in the **Figure.9** .
<div align=center><img width="500" height="550" src="https://user-images.githubusercontent.com/51089749/137869771-50941659-9fc1-450f-ae2a-5628d9b80d2d.png"/></div>
<p align ="center"> <b>Figure9. Example of pipeline.</b></p>

At this part we will explain the function of each pods.
* **triplet-training-pvc:** Provide a volume to save our dataset and model weight.
* **Load data:** We load our dataset and save this file into the pvc volume in the container.
* **Distributed training worker1:** This pod will be deployed under node1 and implement distributed training.
* **Distributed training worker2:** This pod will be deployed under node2 and implement distributed training.
* **Distributed training worker3:** This pod will be deployed under node3 and implement distributed training.
* **Model prediction:** After training, the training program will output the model weight and at this pod need to use this model weight to implement model prediction.(Due to the huge amount of data, this step will take a lot of time.)
* **Serving:** We use flask and html to build a Web UI, user can select image in our [test-image](https://github.com/mike0355/k8s-facenet-distributed-training/tree/main/test-image) folder to upload and implement this application.

### Pod status
As shown in **Figure.10** you can run the following commands to check your pod status.
```commandline
  kubectl get pods --all-namespaces -o wide
```
<div align=center><img width="900" height="100" src="https://user-images.githubusercontent.com/51089749/137872081-491235c7-5511-47b1-a3e1-f25ceb0ad87d.png"/></div>
<p align ="center"> <b>Figure10. Example of pod status.</b></p>

### Port forward
Run the following command and you can turn on your browser.
```commandline
  kubectl port-forward pod/<your pod name> -n kubeflow-user-example-com 8987:8987
```
At address bar you need to input url:
```commandline
  //url
  localhost:8987/upload
```
And the finally, as shown in **Figure.11** , you can enter the web UI page to implement model application.
<div align=center><img width="650" height="450" src="https://user-images.githubusercontent.com/51089749/137875744-ea8f89f0-62ce-4bea-9f4e-d93963d8676d.png"/></div>
<p align ="center"> <b>Figure11. Example of test result.</b></p>

Previous:  [Setup storageclass and PVC](https://github.com/mike0355/k8s-facenet-distributed-training/blob/main/step3_Storageclass_PVC_setting.md)
