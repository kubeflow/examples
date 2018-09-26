FROM python:3.6
MAINTAINER Sven Degroote "sven.degroote@ml6.eu"

# Install python - pip
RUN apt-get update -y && \
    apt-get install -y python3-pip

# Install packages
COPY requirements.txt /
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install tensorflow
RUN pip3 install --upgrade google-cloud-bigquery

COPY . /opt/workdir
WORKDIR /opt/workdir

