
TAG=gcr.io/kubeflow-rl/builder:0.1

docker build -t $TAG .

gcloud docker -- push $TAG
