# Distributed training with Kubeflow pipeline
This example demonstrates how to use kubeflow end-to-end to use Tensorflow MuiltiWorkerMirroredStrategy on the local Kubernetes cluster for distributed training, and implement image similarity calculation through FaceNet algorithm and OpenCV face recognition technology.
## Goals
This tutorial will implement the following items:  
  
*	Use Tensorflow MuiltiWorkerMirroredStrategy to demonstrate distributed training .  
*	Use FaceNet algorithm and OpenCV to implement image similarity calculation .  
  
 At the end of this tutorial, you will learn how to :  
*  Create a new cluster and deploy the Kubeflow on Kubernetes .
*  Install and setup NFS(Network File System) to mount your volume . 
*  Deploy storageclass and pvc to implement dynamic binding .
*  Use Kubeflow Pipeline and Tensorflow CPU to train a distributed model on the cluster .  
*  Use flask server and web UI to implement model application .
  
## The FaceNet and the Model training
  In this tutorial, a algorithm called FaceNet is used to implement a face recognition on K8s. FaceNet presents a algorithm to train the features of Euclidean as a similarity between two face images, and output the distance as the similarity between two face images. In addition, we use triplet loss function to optimized the model.  
  Before training our data, three components are selected as triplets, as shown in **Figure1**, which include an anchor, a positive and a negative from the dataset. Since the model is trained in the Euclidean space, we assume that the distance between two points directly corresponds to the similarity between the two face images. As shown in **Figure2**. after training the model,the distance between the anchor and the positive will be reduced, and that between the anchor and the negative will be increased . 
    
 

<div align=center><img width="700" height="250" src="https://user-images.githubusercontent.com/51089749/137072979-88109170-db18-4803-8422-1673a0887802.png"/></div>
<p align ="center"> <b>Figure1. Example of triplet set.</b></p>
  
<br>

<div align=center><img width="600" height="250" src="https://user-images.githubusercontent.com/51089749/137073084-f5c87f57-5eaa-4f83-89c6-cd97408f8a12.png"/></div>
<p align ="center"><b> Figure2. Distance results before and after training.</b></p>
  
## Test Results
At the end of the training, we use the flask server and web interface to implement the model deployment. As shown in **Figure3**, user can select the face image for similarity calculation from the test images. After clicking the "predict" button, the input image will be in our image database. The similarity of the images is calculated, and the top three ranks are sorted. Each set of ranks contains the distance between the images and the name of the recognized person.
**You can use the test image in [test-image](https://github.com/mike0355/k8s-facenet-distributed-training/tree/main/test-image) folder as the input image.**  
<div align=center><img width="600" height="350" src="https://user-images.githubusercontent.com/51089749/137261141-ec762780-c1db-4b41-8e25-3de9c58b4e2a.png"/></div>
<p align ="center"> <b>Figure3. Example test result.</b></p>

## Steps:
1. [Create a new cluster and deploy the Kubeflow on local Kubernetes](https://github.com/mike0355/k8s-facenet-distributed-training/blob/main/step1_Local_K8s_and_Kubeflow_setup.md)

2. [Install and setup NFS](https://github.com/mike0355/k8s-facenet-distributed-training/blob/main/step2_NFS_setup.md)

3. [Setup storageclass and PVC](https://github.com/mike0355/k8s-facenet-distributed-training/blob/main/step3_Storageclass_PVC_setting.md)

4. [Distributed training on Kubeflow pipeline](https://github.com/mike0355/k8s-facenet-distributed-training/blob/main/step4_Distributed_training.md)

