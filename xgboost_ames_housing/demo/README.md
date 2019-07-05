# kubecon-demo
Kubecon EU 2019 fairing, pipelines demo

1. Launch a notebook

   ```
   kubectl apply -f pvc.kubecon-demo.yaml 
   kubectl apply -f notebook.kubecon-demo.yaml
   ```
1. Attach an extra data volume named 

1. For the CI/CD pipeline you need to create ssh keys

   ```
   kubectl create secret generic kubeflow-bot-ssh-key --from-file=id_rsa=/home/jlewi/.ssh/kubeflow-bot --from-file=id_rsa.pub=/home/jlewi/.ssh/kubeflow-bot.pub 
   ```

1. Create a GITHUB_TOKEN to use with the hub CLI

   ```
   kubectl create secret generic github-token --from-literal=github_token=${GITHUB_TOKEN}
   ```