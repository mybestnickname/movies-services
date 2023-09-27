# syntax=docker/dockerfile:1
FROM python:3.10-slim-buster 

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN addgroup --system app && adduser --system --group app
USER app

WORKDIR /code

RUN pip install --upgrade pip setuptools 
COPY requirements.txt /code/
RUN pip install -r requirements.txt --no-cache-dir

ENV PATH="/home/app/.local/bin:${PATH}"

COPY . /code/
