FROM ubuntu:20.04

LABEL authors="Rafael Sene - rpsene@br.ibm.com"
LABEL year="2021"

RUN apt-get update; apt-get -y install pwgen python3 python3-pip libpq-dev \
python-dev build-essential; pip3 install psycopg2; pip3 install pytz; pip3 install ibm_db

ENV TABLE=""
ENV CLUSTER_ID=""
ENV POWERVS_GUID=""
ENV POWERVS_REGION=""
ENV POWERVS_ZONE=""
ENV OCP_VERSION=""
ENV OCP_SIZE=""
ENV REQUESTOR_EMAIL=""

WORKDIR /python

COPY ./insert.py .

ENTRYPOINT ["/usr/bin/python3", "./insert.py"]
