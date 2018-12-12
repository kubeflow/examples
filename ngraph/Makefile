
GCLOUD_PROJECT ?= none
KUBEFLOW_DIR ?= $$HOME/go/src/github.com/kubeflow/kubeflow
IMG ?= gcr.io/$(GCLOUD_PROJECT)/kubeflow-train
TAG ?= $(eval TAG := $(shell date +v%Y%m-%d-%H-%M))$(TAG)

all: build

build:
	docker build -t $(IMG):$(TAG) --build-arg version=$(TAG) .  && \
	echo push this image by running  && \
	echo TAG=$(TAG) make -e push
	
auth:
	gcloud auth configure-docker
	
push: build
	docker push $(IMG):$(TAG) && \
	echo Pushed $(IMG):$(TAG)

push-latest: push
	gcloud container images add-tag --quiet $(IMG):$(TAG) $(IMG):latest --verbosity=info && \
	echo created $(IMG):latest

run: push
	@./run.sh $(KUBEFLOW_DIR) $(TAG) $(GCLOUD_PROJECT)

clean:
	@./clean.sh $(KUBEFLOW_DIR)

