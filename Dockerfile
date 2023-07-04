ARG BASE_IMAGE=python:3.11-slim

FROM ${BASE_IMAGE} AS builder
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ENV POETRY_VENV=/poetry_venv
RUN python3 -m venv $POETRY_VENV

ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH:$POETRY_VENV/bin"

RUN ${POETRY_VENV}/bin/pip install --upgrade pip && \
        ${VIRTUAL_ENV}/bin/pip install --upgrade pip

RUN ${POETRY_VENV}/bin/pip install poetry

WORKDIR /code
COPY pyproject.toml poetry.lock /code/

RUN ${POETRY_VENV}/bin/poetry install --no-root --without dev

FROM ${BASE_IMAGE} AS base
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV POETRY_VENV=/poetry_venv
ENV PATH="$PATH:$POETRY_VENV/bin"

RUN apt-get update && apt-get upgrade -y

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=builder ${POETRY_VENV} ${POETRY_VENV}

WORKDIR /code

ENTRYPOINT ["lockbox"]

FROM base AS final

COPY . /code

RUN ${POETRY_VENV}/bin/poetry install --without dev

WORKDIR /files

FROM base AS dev

RUN apt-get install -y g++

COPY pyproject.toml poetry.lock /code/
RUN ${POETRY_VENV}/bin/poetry install --no-root

COPY . /code
RUN ${POETRY_VENV}/bin/poetry install

WORKDIR /files
