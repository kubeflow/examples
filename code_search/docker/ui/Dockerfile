ARG BASE_IMAGE_TAG=1.8.0

FROM tensorflow/tensorflow:$BASE_IMAGE_TAG

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - &&\
    apt-get install -y nodejs &&\
    pip install Flask~=1.0.0 \
                nmslib~=1.7.0 \
                numpy~=1.14.0 \
                oauth2client~=4.1.0 \
                requests~=2.18.0 \
                tensor2tensor~=1.7.0 &&\
    rm -rf /var/lib/apt/lists/*

ADD src/ /src

WORKDIR /src

ARG PUBLIC_URL

ENV PUBLIC_URL=$PUBLIC_URL

RUN cd ui && npm i && npm run build && cd ..

EXPOSE 8008

ENTRYPOINT ["python"]
