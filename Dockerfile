# base image is ubuntu
FROM ubuntu:latest
MAINTAINER Mikolaj Figurski <meek.f80@gmail.com>

# Quietly update apt-get list and install python and pip
RUN apt-get -yqq update
RUN apt-get -yqq install python-dev python-pip

# Add work files...
ADD app home/app
WORKDIR home/app

# Quietly pip install requirements...
RUN pip install --quiet -r requirements.txt

EXPOSE 5000

CMD ["python","flaskscript.py"]
