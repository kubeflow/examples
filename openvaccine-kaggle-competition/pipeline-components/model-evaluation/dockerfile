FROM "ubuntu:bionic"
RUN apt-get update 
RUN apt-get upgrade -y
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install tensorflow==2.3.0
RUN pip3 install pandas
RUN pip3 install requests
RUN pip3 install kaggle
RUN pip3 install pickle5

COPY . /
