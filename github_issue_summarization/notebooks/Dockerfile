FROM gcr.io/kubeflow-images-public/tensorflow-1.6.0-notebook-cpu
RUN pip install ktext
RUN pip install annoy
RUN pip install --upgrade google-cloud
RUN pip install sklearn h5py
RUN pip install nltk

COPY ./ /workdir/


ENTRYPOINT ["tini", "--"]
CMD ["sh","-c", "jupyter notebook --notebook-dir=/home/jovyan --ip=0.0.0.0 --no-browser --allow-root --port=8888 --NotebookApp.token='' --NotebookApp.password='' --NotebookApp.allow_origin='*' --NotebookApp.base_url=${NB_PREFIX}"]
