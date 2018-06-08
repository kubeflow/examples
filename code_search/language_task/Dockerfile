# NOTE: The context for this build must be the `language_task` directory

ARG BASE_IMAGE_TAG=1.8.0-py3

FROM tensorflow/tensorflow:$BASE_IMAGE_TAG

ADD requirements.txt /

RUN pip3 --no-cache-dir install -r /requirements.txt

ENV T2T_USR_DIR=/t2t_problems

ADD t2t_problems/* /t2t_problems/