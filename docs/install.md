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

**THIS IS A DRAFT**

Prerequisites

1. Linux machine or VM that can run Docker. We use Digital Ocean, consider using this [referral link](https://www.digitalocean.com/?refcode=7e90b8fb37f8).
2. PostgresSQL, docker, and fig on your host(s).
3. Basic knowledge of Docker, Django, Linux, and nginx or other web server. You should know how to run a basic django app. If not, I highly recommend paying for hosted.

**INSTALL**

1. `git clone https://github.com/burke-software/django-sis` The master branch is always our latest stable. See the develop branch for bleeding edge.
1. Copy fig-production.yml.example to fig-production-yml or other desired location.
2. Edit fig-production.yml and set environment variables for PostgresSQL, email, and any further customizations. For a full list of environment variables see [settings.py](django_sis/settings.py)
3. `fig run --rm web ./manage.py migrate`
4. `fig run --rm web ./manage.py collectstatic`
5. (optional) `fig run --rm web ./manage.py populate_sample_data` This creates a super user/password of aa/aa for convenience.
6. Run docker via fig `fig -f fig-production.sh up`. Obviously you can run the docker images in many other ways. Learn more about how we do it [here](http://davidmburke.com/2014/09/26/docker-in-dev-and-in-production-a-complete-and-diy-guide/).
7. It should now be running on port 8000. Consider changing the port in fig-production.yml, using nginx as a proxy, and using SSL with nginx. We also recommend not storing media or static files in docker even though fig does support persistence. Use S3 or mount a volume for media. To use S3 just set the related variables as defined in [settings.py](django_sis/settings.py).

## Running Schooldriver without Docker.

**Not recommended**

1. Base system must be Ubuntu 12.04 in order to use libreoffice document conversion. 14.04 does not support python-uno with python2.
2. Do everything in [Dockerfile](Dockerfile)
3. Set up environment variables or extend settings directly by editing /django-sis/settings_local.py.
4. Make sure to set up Redis and PostgresSQL. 
5. Run Celery worker(s)
5. Deploy with your favorite web server. See run-production.sh for an example.

# Upgrading

1. `git pull origin master` to get the latest code
2. `fig build` to build any new requirements
3. `fig run --rm web ./manage.py migrate` to migrate the database
4. `fig run --rm web ./manage.py collectstatic` to update static files
5. Restart fig/docker or your web server/celery if using such.
