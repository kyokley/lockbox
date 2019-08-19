FROM python:3.7-slim
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ARG REQS=--no-dev

RUN apt-get update && apt-get install -y curl gnupg

ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN echo 'export PATH=$PATH:/root/.poetry/bin' >> /root/.bashrc
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
RUN pip install -U pip

WORKDIR /code
COPY pyproject.toml /code/pyproject.toml
COPY poetry.lock /code/poetry.lock


RUN /bin/bash -c "/root/.poetry/bin/poetry install ${REQS}"
RUN python setup.py install

COPY . /code

WORKDIR /files

ENTRYPOINT ["lockbox"]
