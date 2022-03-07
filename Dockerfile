FROM python:3.8.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

RUN mkdir /TLS

CMD [ "python3", "app.py"]