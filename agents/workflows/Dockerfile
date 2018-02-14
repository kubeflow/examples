FROM docker:17.10

RUN apk update

RUN apk add --no-cache curl
RUN apk add bash
RUN apk add --update \
    python

RUN curl https://sdk.cloud.google.com | bash
