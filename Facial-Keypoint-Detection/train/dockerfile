FROM "ubuntu:bionic"
RUN apt-get update && yes | apt-get upgrade
RUN mkdir -p /tensorflow/models
RUN apt-get install -y git python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install tensorflow
RUN pip3 install jupyter
RUN pip3 install matplotlib
RUN pip3 install kfp==1.1.2
RUN pip install opencv-python-headless
RUN pip3 install pandas keras 
RUN pip3 install sklearn
RUN pip3 install autokeras
COPY . /