FROM tensorflow/tensorflow:1.11.0

# Install wget
RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

# Install hypertune package and yaml package
RUN pip install --upgrade cloudml-hypertune
RUN pip install ruamel.yaml

# Installs google cloud sdk, this is mostly for using gsutil to export model.
RUN wget -nv \
    https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz && \
    mkdir /root/tools && \
    tar xvzf google-cloud-sdk.tar.gz -C /root/tools && \
    rm google-cloud-sdk.tar.gz && \
    /root/tools/google-cloud-sdk/install.sh --usage-reporting=false \
        --path-update=false --bash-completion=false \
        --disable-installation-options && \
    rm -rf /root/.config/* && \
    ln -s /root/.config /config && \
    # Remove the backup directory that gcloud creates
    rm -rf /root/tools/google-cloud-sdk/.install/.backup

# Path configuration
ENV PATH $PATH:/root/tools/google-cloud-sdk/bin
# Make sure gsutil will use the default service account
#RUN echo '[GoogleCompute]\nservice_account = default' > /etc/boto.cfg
RUN rm -rf /etc/boto.cfg

# Create directory and copy the source code.
RUN mkdir -p /root/linear_learner/
# Create model directory. This is where all the model artifacts will reside.
# This will be uploaded to user's GCS bucket.
RUN mkdir -p /root/export/
# Create pre processed data directory. This is where the processed data will
# reside. This will be uploaded to user's GCS bucket.
RUN mkdir -p /root/processed_data/

COPY src/task.py /root/linear_learner/
COPY src/model.py /root/linear_learner/
COPY src/data_utils.py /root/linear_learner/
COPY src/hypertune_hook.py /root/linear_learner/
COPY src/__init__.py /root/linear_learner/
COPY src/training_task.py /root/linear_learner/
COPY src/preprocessor.py /root/linear_learner/

WORKDIR /root

ENTRYPOINT ["python", "linear_learner/task.py"]