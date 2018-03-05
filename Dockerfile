FROM python:2.7

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install pytest

COPY . /app
RUN pip install -e .
CMD pytest
