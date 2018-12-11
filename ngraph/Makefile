
GCLOUD_PROJECT ?= none
BUCKET ?= $(eval BUCKET := $(shell whoami)-$(shell printf "%06x\n" $$RANDOM))$(BUCKET)
IMG ?= gcr.io/$(GCLOUD_PROJECT)/kubeflow-train
TAG ?= $(eval TAG := $(shell date +v%Y%m-%d-%H-%M))$(TAG)
IAM_EMAIL ?= kubeflow-codelab@$(GCLOUD_PROJECT).iam.gserviceaccount.com

all: build

buckets:
	@./bucket.sh list

create-bucket:
	@./bucket.sh create $(BUCKET) $(IAM_EMAIL)

delete-bucket:
	@./bucket.sh delete $(BUCKET)

delete-buckets:
	@./bucket.sh delete all

build:
	docker build -t $(IMG):$(TAG) --build-arg version=$(TAG) --build-arg bucket=$(BUCKET) .  && \
	echo push this image by running  && \
	echo TAG=$(TAG) BUCKET=$(BUCKET) make -e push
	
auth:
	gcloud auth configure-docker
	
push: create-bucket build
	docker push $(IMG):$(TAG) && \
	echo Pushed $(IMG):$(TAG)

push-latest: push
	gcloud container images add-tag --quiet $(IMG):$(TAG) $(IMG):latest --verbosity=info && \
	echo created $(IMG):latest

run: clean push
	@./run.sh $(TAG)

clean:
	@./bucket.sh delete all
	@kf delete

