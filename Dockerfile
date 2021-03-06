# Suggest running this as 'app'
# Before running, the database server ('db') must first be started

FROM python:3.5

ENV PYTHONUNBUFFERED 1
ENV DJANGO_CONFIGURATION Docker
ENV HOME /root

# DB Configuration
# ENV DB_NAME=postgres
# ENV DB_PASSWORD=
# ENV DB_USER=postgres
# ENV DB_HOST=db
# ENV DB_PORT=5432

# Salesforce configuration
# ENV SALESFORCE_USERNAME=none
# ENV SALESFORCE_PASSWORD=none
# ENV SALESFORCE_TOKEN=none

# Project identifier configuration
# ENV PROJECT_IDENTIFIER_PREFIX=GM
# ENV PROJECT_IDENTIFIER_START=100

# Listen host/port configuration
ENV LISTEN_HOST=0.0.0.0
ENV LISTEN_PORT=8000
ENV REDIS_URL=redis://redis:6379

ENV DOCKERIZE_VERSION v0.3.0
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Grab libxml2 and libxslt for snekbol
RUN apt-get update && apt-get -q -y install libxml2-dev libxslt-dev

WORKDIR /usr/src/app
RUN mkdir lims
COPY . lims
WORKDIR /usr/src/app/lims
RUN pip install -r requirements.txt

CMD ["sh", "-c", "gunicorn lims.wsgi -w 2 -b $LISTEN_HOST:$LISTEN_PORT --log-level -"]

