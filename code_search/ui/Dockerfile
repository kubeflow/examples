FROM node:10.6

EXPOSE 5000

RUN npm i -g serve

ADD ./build /webapp

ENTRYPOINT ["serve"]

CMD ["-l", "5000", "-n", "/webapp"]
