

docker build $TAG .

gcloud docker -- push $TAG
