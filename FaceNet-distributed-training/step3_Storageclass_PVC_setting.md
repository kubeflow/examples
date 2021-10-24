## Storageclass and PVC.
In this part, we need to use storageclass to implement dynamic binding. The definition of dynamic binding is to realize the action of PVC binding without editing PV by yourself, which is more efficient than editing PV to do static binding.
  
Deploy NFS provisioner.yaml on the Kubernetes. We already provided NFS [provisioner](https://github.com/mike0355/k8s-facenet-distributed-training/blob/main/NFS-setting/deployment.yaml) file, so you only need to modify NFS server and NFS client's IP and mount directory folder location, as shown in **Figure.1**
<div align=center><img width="650" height="250" src="https://user-images.githubusercontent.com/51089749/137686605-471c8cc2-7c8f-4e62-8964-145bcdbfeb92.png"/></div>
<p align ="center"> <b>Figure1. Example of provisioner.</b></p>
  
  
After edit NFS provisioner, following this command to deploy and check your NFS provisioner, as shown in **Figure.2**
```commandline
  //deploy
  kubectl create -f (your YAML file name)
  
  // check your file
  kubectl get deployment
```
<div align=center><img width="850" height="100" src="https://user-images.githubusercontent.com/51089749/137687897-69860a6a-74ac-4daf-949a-8ab54d478ad3.png"/></div>
<p align ="center"> <b>Figure2. Example of deploy porvisioner.</b></p>
  
Create storageclass.yaml, we already provided [storageclass](https://github.com/mike0355/k8s-facenet-distributed-training/blob/main/NFS-setting/class.yaml) file so you no need to rewrite a new one, but if you want to modify your storageclass name, you can modify at the position of the red box in **Figure.3**
<div align=center><img width="850" height="200" src="https://user-images.githubusercontent.com/51089749/137688313-4aed0b1b-b46c-450e-bc14-fcceb552a130.png"/></div>
<p align ="center"> <b>Figure3. Example of storageclass.</b></p>
  
After edit storageclass, following this command to deploy and check your storageclass, as shown in **Figure.4**.
```commandline
  //deploy
  kubectl create -f (your YAML file name)
  
  // check your file
  kubectl get storageclass
```
<div align=center><img width="850" height="100" src="https://user-images.githubusercontent.com/51089749/137689385-1de834bb-5e4d-4acc-8115-a0287f151df9.png"/></div>
<p align ="center"> <b>Figure4. Example of deploy storageclass.</b></p>

Add NFS-client-provisioner as the authority source for NFS provisioner, we already provided [ServiceAccount](https://github.com/mike0355/k8s-facenet-distributed-training/blob/main/NFS-setting/rbac.yaml) file so you no need to rewrite a new one. In Kubernetes, we use Role, RoleBinding, ClusterRole, ClusterRoleBinding is used to give the service account sufficient permissions to handle the work related to StorageClass and PersistentVolumeClaim (PVC).
  
Following the commands to deploy and check your serviceaccount, as shown in **Figure.5**
```commandline
  //deploy
  kubectl create -f (your YAML file name)
  
  // check your file
  kubectl get ServiceAccount
```
<div align=center><img width="850" height="150" src="https://user-images.githubusercontent.com/51089749/137692316-710a4f42-b00b-4a08-a852-89c3918dc5e3.png"/></div>
<p align ="center"> <b>Figure5. Example of deploy ServiceAccount.</b></p>
  
Most of the settings are completed, you can deploy our [test-claim](https://github.com/mike0355/k8s-facenet-distributed-training/blob/main/NFS-setting/test-claim.yaml) to confirm whether the PVC will be created under the mount directory of the NFS server

<div align=center><img width="850" height=250" src="https://user-images.githubusercontent.com/51089749/137693565-39f139c6-9d41-4e28-b9d4-b4a0f2301874.png"/></div>
<p align ="center"> <b>Figure6. Example of test-claim.</b></p>

Previous: [Install and setup NFS](https://github.com/mike0355/k8s-facenet-distributed-training/blob/main/step2_NFS_setup.md)
  
Next: [Distributed training on Kubeflow pipeline](https://github.com/mike0355/k8s-facenet-distributed-training/blob/main/step4_Distributed_training.md)
