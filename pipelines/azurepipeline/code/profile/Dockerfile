FROM tensorflow/tensorflow:2.0.0a0-gpu-py3
RUN pip install --upgrade pip pillow && \
    pip install azureml-sdk==1.1.5.1 azure-cli==2.2.0
RUN az extension add -n azure-cli-ml
COPY profile.sh /scripts/profile.sh
COPY inferenceconfig.json /scripts/inferenceconfig.json
COPY score.py /scripts/score.py
COPY environment.yml /scripts/environment.yml

ENTRYPOINT bash