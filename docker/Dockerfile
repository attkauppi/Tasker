FROM python:3.8.1-slim-buster

# work dir
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install netcat -y

# depends
RUN pip install --upgrade pip
RUN pip install wheel
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# Copy
COPY . /usr/src/app
RUN chmod +x /usr/src/app/entrypoint.sh

# Entrypoint
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]