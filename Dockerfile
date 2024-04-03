FROM python:3.12-slim
LABEL maintainer="maksym.symonovych@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


COPY . .

