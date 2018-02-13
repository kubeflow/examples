FROM alpine:3.7
ENV AWS_ENDPOINT_URL=""
RUN apk --update add python py-pip \
      groff less mailcap && \
    pip install --upgrade awscli==1.14.37 s3cmd==2.0.1 python-magic && \
    apk --purge del py-pip && rm /var/cache/apk/*
VOLUME /root/.aws
COPY aws_wrapper /bin/aws_wrapper
ENTRYPOINT ["aws_wrapper"]
