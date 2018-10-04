all: download dep export

download:
	./download_v3_checkpoint.sh
dep:
	pip install -r requirements.txt
export:
	python export_inception_v3.py --output_dir=gs://kubeflow/inception --model_version=2
