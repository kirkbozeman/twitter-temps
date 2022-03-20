FROM python:3.7-slim-buster

RUN apt-get update --fix-missing \
    && apt-get install -y \
        libgeos-dev gcc \
        vim \
        sudo

WORKDIR /root
RUN pip install --upgrade pip
ADD requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir app && \
    mkdir output && \
    mkdir testing
ADD /app app
ADD /tests tests

CMD ["python", "-u", "app/core.py"]