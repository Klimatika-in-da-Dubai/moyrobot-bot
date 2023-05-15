FROM python:3.10-buster

RUN apt-get install tzdata
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app


CMD python -m app