FROM python:3.6

RUN pip install --upgrade ktext annoy sklearn nltk tensorflow
RUN pip install --upgrade matplotlib ipdb
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install unzip
RUN mkdir /issues
WORKDIR /issues
COPY . /issues
RUN chmod +x /issues/download.sh
RUN mkdir /model
RUN mkdir /data

CMD python train.py
