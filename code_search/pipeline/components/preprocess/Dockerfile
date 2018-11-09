FROM python:2

RUN git clone --branch=master --depth=1 https://github.com/kubeflow/examples && \
    python2 -m pip install --user -r examples/code_search/src/requirements.txt && \
    # https://github.com/kubeflow/examples/issues/321
    python2 -m spacy download en

# Downloading gcloud package
RUN curl https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > /tmp/google-cloud-sdk.tar.gz

# Installing the package
RUN mkdir -p /usr/local/gcloud \
  && tar -C /usr/local/gcloud -xvf /tmp/google-cloud-sdk.tar.gz \
  && /usr/local/gcloud/google-cloud-sdk/install.sh

# Adding the package path to local
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

WORKDIR examples/code_search/src

ENTRYPOINT ["/bin/bash", "-c", "gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS} && python2 -m code_search.dataflow.cli.preprocess_github_dataset"]
