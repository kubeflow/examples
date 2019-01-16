FROM gcr.io/kubeflow-images-public/tensorflow-1.6.0-notebook-cpu
RUN pip install ktext annoy sklearn h5py nltk
RUN pip install --upgrade google-cloud
COPY ./ /workdir/
