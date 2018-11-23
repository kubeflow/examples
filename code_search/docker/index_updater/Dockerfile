FROM ubuntu:xenial

RUN apt-get update && apt-get install -y wget &&\
    rm -rf /var/lib/apt/lists/*

RUN wget -O /tmp/hub-linux-amd64-2.6.0.tgz https://github.com/github/hub/releases/download/v2.6.0/hub-linux-amd64-2.6.0.tgz && \
	cd /usr/local && \
	tar -xvf /tmp/hub-linux-amd64-2.6.0.tgz && \
	ln -sf /usr/local/hub-linux-amd64-2.6.0/bin/hub /usr/local/bin/hub
