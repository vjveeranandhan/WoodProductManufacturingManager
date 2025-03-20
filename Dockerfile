FROM python:3.10.12-slim-buster

WORKDIR /app

# Use a base image (adjust this according to your project needs)
FROM python:3.10-slim

# Update and install dependencies
RUN apt-get update && \
    apt-get install -y build-essential wget

# Download and extract SQLite 3.31.0
RUN wget https://www.sqlite.org/2020/sqlite-autoconf-3310000.tar.gz && \
    tar xvf sqlite-autoconf-3310000.tar.gz && \
    cd sqlite-autoconf-3310000 && \
    ./configure && \
    make && \
    make install

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

# Clean up to reduce image size
RUN rm -rf sqlite-autoconf-3310000.tar.gz sqlite-autoconf-3310000

COPY . .

CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]

