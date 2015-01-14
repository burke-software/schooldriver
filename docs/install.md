# Installation

Schooldriver is not yet stable. We're hoping to make a stable official release in Feb 2015. 
Right now git master is as stable as it gets. We recommend paying for hosting if you need stability.

## Requirements

We highly suggest using Docker which takes care of most requirements. 
Schooldriver is a large application and we do not support using alternative versions of Django and other libraries. 
However it should be possible to run as a typical django app without Docker. Check out *requirements.txt for specific requirements.

You need:

- PostgreSQL with hstore enabled (We don't suggest using postgres in docker in production environments) MySQL is not supported.
- Ram depends on the number of users. You probably need at least 1GB. 2GB is recommended for more than 400 users.

## Running Schooldriver with Docker in production

More coming soon :) `fig up` works but isn't good for production.

DRAFT STEPS:

1. Install PostgresSQL
2. Set environment variables for PostgresSQL, email, and any further customizations.
3. `fig run --rm web ./manage.py migrate`
4. (optional) `fig run --rm web ./manage.py populate_sample_data`
5. Run docker images as described in fig.yml.

## Running Schooldriver without Docker.

1. Base system must be Ubuntu 12.04 in order to use libreoffice document conversion. 14.04 does not support python-uno with python2.
2. Install everything in the multiple requirements.txt files
3. Set up environment variables or extend settings directly by editing /django-sis/settings_local.py.
4. Make sure to set up Redis and PostgresSQL. 
5. Deploy with your favorite web server. See run-production.sh for an example.
