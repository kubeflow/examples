FROM python:3.7

COPY . /app/

RUN pip3 install --no-cache-dir -r /app/requirements.txt

ENTRYPOINT ["python3", "/app/text_classification_rnn.py"]