# Clean Kubeflow v1.2 (Minikube)
> kubeflow v1.2 cannot be directly upgraded to kubeflow v1.3, you need to delete kubeflow v1.2 and install kubeflow v1.3. \
> **Don't forget to back up your files.**

### Step 1：Delete minikube environment
```Bash
minikube stop
minikube delete --purge
```

### Step 2：Delete docker image
```Bash
docker system prune -a
```

### Step 3：Delete instruction packet
```Bash
cd /usr/local/bin/
sudo rm -rf *
```

### Step 4：Enable boot cleanup
```Bash
cd /usr/lib/tmpfiles.d
sudo gedit tmp.conf
```
In line 11, uncommented indicates that startup cleanup is enabled, and comment indicates that startup cleanup is not enabled. \
<img src="https://github.com/WEICHINLIN/Kubeflow---Natural-Language-Processing/blob/main/4.%20Image/boot%20cleanup.png" alt="ls -l no"/><br/>
Ctrl + s Save after modification.

# Install Kubeflow v1.3 (First minikube start)

### Step 1：Open the terminal
You must make sure you can find the following files when typing ls -l on the terminal.
```Bash
ls -l
```
<img src="https://github.com/WEICHINLIN/Kubeflow---Natural-Language-Processing/blob/main/4.%20Image/ls%20-l%20no.png" alt="ls -l no"/><br/>
Then you can proceed to the next step.

### Step 2：Give execution permission
```Bash
sudo chmod +x docker.sh
sudo chmod +x minikube.sh
sudo chmod +x kubeflow.sh
```
or
```Bash
sudo chmod +x *.sh
```
If successful, the file name will turn green. \
<img src="https://github.com/WEICHINLIN/Kubeflow---Natural-Language-Processing/blob/main/4.%20Image/ls%20-l%20yes.png" alt="ls -l yes"/><br/>
Then you can proceed to the next step.

### Step 3：sudo ./docker.sh
```Bash
sudo ./docker.sh
```
reboot VM or computer. \
Then confirm the docker version. \
<img src="https://github.com/WEICHINLIN/Kubeflow---Natural-Language-Processing/blob/main/4.%20Image/docker%20version.png" alt="docker version"/><br/>
If you can see Clinet and Server versions, it means success.

### Step 4：sudo ./minikube.sh
```Bash
sudo ./minikube.sh
```
After success, you will see the following screen. (first time)\
<img src="https://github.com/WEICHINLIN/Kubeflow---Natural-Language-Processing/blob/main/4.%20Image/first%20minikube.png" alt="first minikube"/><br/>
Next, you can change the owner of the .kube and .minikube folders. \
In this way, subsequent commands related to kubectl and minikube do not need to add sudo. \
The line with the second red exclamation mark indicates the storage location of .kube and .minikube.
```Bash
sudo chown -R <user_name> .kube .minikube
```
You can enter ls -l -a to confirm, the first name is the owner and the second name is the group.
```Bash
ls -l -a
```
<img src="https://github.com/WEICHINLIN/Kubeflow---Natural-Language-Processing/blob/main/4.%20Image/chown.png" alt="chown"/><br/>
It’s okay if you don’t do this step to change the owner, you can skip it directly.

### Step 5：sudo ./kubeflow.v13.sh
```Bash
sudo ./kubeflow.v13.sh
```
After execution, enter the following command to observe the pods status:
```Bash
kubectl get pods -n kubeflow
```
<img src="https://github.com/WEICHINLIN/Kubeflow---Natural-Language-Processing/blob/main/4.%20Image/get%20pods.png" alt="get pods"/><br/>
It takes about 30 minutes to wait for 16G RAM. \
After seeing the same situation as on the screen, you can proceed to the next step.

### Step 6：Port-forward
After all the pods are running
```Bash
kubectl port-forward -n istio-system svc/istio-ingressgateway 8080:80
```
Input in the browser
```Bash
http://localhost:8080/
```
or
```Bash
127.0.0.1:8080
```
<img src="https://github.com/WEICHINLIN/Kubeflow---Natural-Language-Processing/blob/main/4.%20Image/login.png" alt="login"/><br/>
* Email Address：user@example.com
* Password：12341234

<img src="https://github.com/WEICHINLIN/Kubeflow---Natural-Language-Processing/blob/main/4.%20Image/kubeflow%20home.png" alt="kubeflow home"/><br/>

### Step 7：Disable boot cleanup
```Bash
cd /usr/lib/tmpfiles.d
sudo gedit tmp.conf
```
In line 11, uncommented indicates that startup cleanup is enabled, and comment indicates that startup cleanup is not enabled. \
<img src="https://github.com/WEICHINLIN/Kubeflow---Natural-Language-Processing/blob/main/4.%20Image/boot%20cleanup%20up.png" alt="ls -l no"/><br/>
Ctrl + s Save after modification.
> Kubeflow installed on Minikube will store data in /tmp/hostpath-provisioner. \
> The data in /tmp will be deleted after shutdown. \
> To ensure that the data is not deleted, this function needs to be disabled.

# Second minikube start
> After the installation is complete and startup cleanup is disabled, you can shut down your computer without worrying about data loss.
After restarting the computer or virtual machine, enter:
```Bash
minikube stop
```
Close Minikube completely, and enter:
```Bash
minikube start
```
Wait for Minikube to start. \
<img src="https://github.com/WEICHINLIN/Kubeflow---Natural-Language-Processing/blob/main/4.%20Image/second%20minikube.png" alt="second minikube"/><br/>
After starting, confirm whether the Pod is running. After running, you can execute port-forward.

# Relevant part

* [About Version](https://github.com/dfm871002/examples/blob/master/Natural-Language-Processing/README.md)
* [About Docker](https://github.com/dfm871002/examples/blob/master/Natural-Language-Processing/2.%20Docker/Docker.md)
* [About Jupyter Notebook](https://github.com/dfm871002/examples/blob/master/Natural-Language-Processing/3.%20Jupyter%20Notebook/Jupyter%20Notebook.md)
