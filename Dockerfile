ARG BASE_IMAGE=python:3.12-slim

FROM ${BASE_IMAGE} AS base
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=.

RUN pip install uv

WORKDIR /code
COPY pyproject.toml uv.lock /code/

RUN uv sync --frozen --no-dev

WORKDIR /code

COPY . /code

ENTRYPOINT ["uv", "run", "--no-sync", "python", "scripts/lockbox.py"]

FROM base AS dev
RUN uv sync --frozen
