FROM python:3.5.1-alpine

# source code
RUN mkdir -p /srv/src
ADD . /srv/src
WORKDIR /srv/src

# create new directory to store gunicorn logs
RUN mkdir -p /var/log/gunicorn

# dependencies
RUN pip install -r requirements.txt
