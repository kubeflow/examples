FROM "ubuntu:bionic"
RUN apt-get update && yes | apt-get upgrade
RUN mkdir -p /tensorflow/models
RUN apt-get install -y git python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install pandas keras 
RUN pip3 install autokeras
COPY . /