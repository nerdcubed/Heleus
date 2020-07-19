FROM python:3.8.4-buster

RUN adduser --disabled-password --disabled-login python
WORKDIR /app

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN apt update && apt -y install libffi-dev python3.7-dev && \
    pip3 install -U pipenv uvloop && \
    pipenv install --deploy --system && \
    rm -rf /var/lib/apt/lists/*

RUN chown -R python:python /app
USER python

COPY --chown=python:python ./cogs ./cogs
COPY --chown=python:python ./utils ./utils
COPY --chown=python:python ./heleus.py ./heleus.py

CMD ["python", "-u", "./heleus.py", "--uvloop"]
