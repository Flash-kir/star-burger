FROM python:3.9-slim-bullseye
WORKDIR /star-burger
COPY ./requirements.txt .
RUN apt-get update
RUN apt-get --force-yes -y install git gcc libpq-dev postgresql-client-common postgresql-common
RUN pip install -r requirements.txt
COPY . .