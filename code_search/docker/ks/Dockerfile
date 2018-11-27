FROM debian:7

RUN apt-get update -q && apt-get upgrade -y && \
    apt-get install -y -qq --no-install-recommends \
      ca-certificates \
      wget && \
    wget -O /opt/ks_0.12.0_linux_amd64.tar.gz \
      https://github.com/ksonnet/ksonnet/releases/download/v0.12.0/ks_0.12.0_linux_amd64.tar.gz && \
    tar -C /opt -xzf /opt/ks_0.12.0_linux_amd64.tar.gz && \
    cp /opt/ks_0.12.0_linux_amd64/ks /bin/. && \
    rm -f /opt/ks_0.12.0_linux_amd64.tar.gz && \
    wget -O /bin/kubectl \
      https://storage.googleapis.com/kubernetes-release/release/v1.11.2/bin/linux/amd64/kubectl && \
    chmod u+x /bin/kubectl

ADD kubeflow /usr/local/src
ADD docker/ks/search_index_creator.sh /usr/local/src
ADD docker/ks/submit_code_embeddings_job.sh /usr/local/src
ADD docker/ks/initialize_kubectl.sh /usr/local/src
ADD docker/parse_arguments.sh /usr/local/src

WORKDIR /usr/local/src
