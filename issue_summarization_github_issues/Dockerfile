FROM gcr.io/kubeflow/tensorflow-notebook-cpu:v1

USER root

RUN conda update -y pandas && \
  pip install ktext==0.31 && \
  pip install annoy==1.10.0 && \
  pip install nltk==3.2.5 && \
  pip install pydot==1.2.3 && \
  pip install pydot-ng==1.0.0 && \
  pip install graphviz==0.8.1 && \
  apt-get install -y graphviz

USER jovyan

COPY --chown=jovyan:users notebooks notebooks
