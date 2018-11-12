FROM debian

ADD src/code_search /app/code_search
ADD .             /src

ADD kubeflow /usr/local/src
ADD docker/ks/deploy.sh /usr/local/src

WORKDIR /usr/local/src
