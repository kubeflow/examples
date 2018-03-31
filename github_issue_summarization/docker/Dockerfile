FROM python:alpine

COPY ./flask_web/requirements.txt /app/

WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install requests

COPY ./flask_web /app

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]

