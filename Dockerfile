FROM ubuntu:12.04
ENV PYTHONUNBUFFERED 1
RUN apt-get update -qq && apt-get install -y python-psycopg2 libldap2-dev libsasl2-dev libpq-dev postgresql-client git-core coffeescript python-uno python-pip python-dev g++
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
ADD dev-requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install -r dev-requirements.txt
ADD . /code/
