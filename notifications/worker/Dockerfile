FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN python -m pip install --upgrade pip
RUN pip install --upgrade setuptools
COPY requirements.txt /code/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /code/app

ENV PYTHONPATH "${PYTHONPATH}:/code/app"

CMD python app/main.py
