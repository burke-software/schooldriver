FROM python:2
ENV PYTHONUNBUFFERED 1
RUN apt-get update -qq && apt-get install -y python-psycopg2 postgresql-client git-core coffeescript
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
