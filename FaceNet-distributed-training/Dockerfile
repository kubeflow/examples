FROM tensorflow/tensorflow
RUN apt-get -y update
RUN python -m pip install --user --upgrade pip
RUN pip3 install --user requests
RUN apt-get install cmake -y
RUN pip3 install --user numpy
RUN pip3 install --user keras
RUN pip3 install --user scikit-learn
RUN pip3 install --user cmake
RUN pip3 install --user flask
RUN pip3 install --user seaborn
RUN pip3 install --user dlib
RUN pip3 install --user opencv-python==4.1.1.26
RUN pip3 install --user opencv-contrib-python-headless==4.1.1.26
RUN pip3 install --user imutils
RUN pip3 install --user tqdm
RUN pip3 install --user matplotlib
RUN pip3 install --user tensorflow_datasets
ADD k8s_facenet_distributedtraining ./


