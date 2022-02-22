FROM python:3.10.2-buster

RUN adduser --disabled-password --disabled-login --gecos '' python
WORKDIR /app

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN apt update && apt -y install libffi-dev && \
    pip3 install -U pip poetry && \
    poetry config virtualenvs.create false && \
    poetry install && \
    rm -rf /var/lib/apt/lists/*

RUN chown -R python:python /app
USER python

COPY --chown=python:python ./cogs ./cogs
COPY --chown=python:python ./utils ./utils
COPY --chown=python:python ./heleus.py ./heleus.py

CMD ["python", "-u", "./heleus.py", "--uvloop"]
