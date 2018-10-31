FROM tensorflow/tensorflow

USER root

WORKDIR /

# To allow running it locally.  See local_run.sh.
RUN touch /credentials.json

ADD *.py /

ENTRYPOINT ["python", "work.py"]
