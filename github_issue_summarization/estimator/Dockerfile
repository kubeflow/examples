FROM python:3.6

RUN pip install --upgrade ktext annoy sklearn nltk tensorflow
RUN pip install --upgrade matplotlib ipdb
ENV DEBIAN_FRONTEND=noninteractive
RUN mkdir /issues
WORKDIR /issues
COPY . /issues
RUN mkdir /model
CMD python train.py
