FROM orchardup/python:2.7
ENV PYTHONUNBUFFERED 1
RUN apt-get update -qq && apt-get install -y python-psycopg2 libpq-dev postgresql-client git-core coffeescript
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
ADD dev-requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install -r dev-requirements.txt
ADD . /code/
