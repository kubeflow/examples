FROM tensorflow/tensorflow

RUN pip install PyYaml google-cloud-storage

USER root

WORKDIR /

RUN touch /credentials.json

ADD *.py /

ADD params.yaml /

ENTRYPOINT ["python", "work.py"]
