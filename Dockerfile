ARG BASE_IMAGE=python:3.11-slim

FROM ${BASE_IMAGE} AS builder
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ENV POETRY_VENV=/poetry_venv
RUN python3 -m venv $POETRY_VENV

ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH:$POETRY_VENV/bin"

RUN ${POETRY_VENV}/bin/pip install poetry

WORKDIR /code
COPY pyproject.toml poetry.lock /code/
RUN ${POETRY_VENV}/bin/poetry install --without dev

ENTRYPOINT ["lockbox"]

FROM ${BASE_IMAGE} AS final
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /code

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

FROM final AS dev
ENV POETRY_VENV=/poetry_venv
ENV PATH="$PATH:$POETRY_VENV/bin"

COPY --from=builder ${POETRY_VENV} ${POETRY_VENV}
COPY . /code
RUN ${POETRY_VENV}/bin/poetry install
