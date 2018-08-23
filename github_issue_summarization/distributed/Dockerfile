FROM python:3.6

RUN pip install --upgrade ktext annoy sklearn nltk tensorflow
RUN pip install --upgrade matplotlib ipdb
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install unzip
RUN mkdir /issues
WORKDIR /issues
COPY distributed /issues
COPY notebooks/seq2seq_utils.py /issues
COPY ks-kubeflow/components/download_data.sh /issues
RUN chmod +x /issues/download_data.sh
RUN mkdir /model
RUN mkdir /data

CMD python train.py
