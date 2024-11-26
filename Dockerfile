FROM python:3.11-slim-buster

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DLX_REST_PRODUCTION="True"

# set working directory
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN apt-get update && apt-get install -y git
RUN pip install -r requirements.txt
RUN pip install gunicorn

# add app
COPY . /usr/src/app

CMD ["gunicorn", "--bind", ":5000", "--timeout", "900", "ods:app"]