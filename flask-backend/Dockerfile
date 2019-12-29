FROM python:3.6.8
ADD . /simpleFlaskApp
WORKDIR /simpleFlaskApp
RUN apt-get update && apt-get install vim -y
RUN pip install -r requirements.txt
