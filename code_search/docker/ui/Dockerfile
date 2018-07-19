FROM node:10.6

ADD ui/ /ui

WORKDIR /ui

RUN npm i && npm run build && npm i -g serve

EXPOSE 5000

ENTRYPOINT ["serve"]

CMD ["-l", "5000", "-n", "/ui/build"]
