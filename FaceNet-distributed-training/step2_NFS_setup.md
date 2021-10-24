# Network File System Setup
 In this part, you need to install Network File System (NFS) and setup your NFS server. This is very helpful for the subsequent steps, because distributed training will finally return the trained data to the NFS folder, and after all machines are trained, they will be consolidated into a weight file.
## Install Network File System (NFS)
Install the NFS server on your server, and install the NFS command on your client.

```commandline
//NFS Server
sudo apt-get install nfs-kernel-server

//NFS Client
sudo apt-get install nfs-common
```
On the server and client, you need to create the mount directory and give permission.

```commandline
//NFS Server
 mkdir  –p  /mnt/ (your mount directory folder name on the server)
 chmod  -R 777 /mnt/ (your mount directory folder name on the server)
 
//NFS Client
 mkdir  –p  /mnt/ (your mount directory folder name on the client)
 chmod  -R 777 /mnt/ (your mount directory folder name on the client)
```
Add the mount directory location and IP address of the client computer and server under **/etc/exports** path, as shown in **Figure.1**.
```commandline
 cd /etc
 sudo gedit exports
```
<div align=center><img width="650" height="150" src="https://user-images.githubusercontent.com/51089749/137679487-f55ff7a5-4171-474c-b278-812218f32679.png"/></div>
<p align ="center"> <b>Figure1. Example of export data.</b></p>

Finally, turn on your NFS server and check your NFS system status, as shown in **Figure.2**, if the NFS server displays a green light, it means it has successfully started.

```commandline
sudo service nfs-server start
sudo service nfs-server status
```
<div align=center><img width="650" height="150" src="https://user-images.githubusercontent.com/51089749/137680172-765eb902-05c4-4e04-84f8-1e7e17ea410c.png"/></div>
<p align ="center"> <b>Figure2. Example of NFS server status.</b></p>

After the previous settings, run the following command and you can mount files from the server on the client side, as shown in **Figure.3**.
```commandline
 sudo mount -t nfs (NFS Server IP):/mnt/(your mount directory folder name on the server)  /mnt/(your mount directory folder name on the client) -o nolock
```
<div align=center><img width="650" height="250" src="https://user-images.githubusercontent.com/51089749/137680883-299a1daf-e52b-4eed-95a8-46511b6fd826.png"/></div>
<p align ="center"> <b>Figure3. Example of show mount directory.</b></p>

Previous: [Create a new cluster and deploy the Kubeflow on local Kubernetes](https://github.com/mike0355/k8s-facenet-distributed-training/blob/main/step1_Local_K8s_and_Kubeflow_setup.md)
  

Next: [Setup storageclass and PVC](https://github.com/mike0355/k8s-facenet-distributed-training/blob/main/step3_Storageclass_PVC_setting.md)

