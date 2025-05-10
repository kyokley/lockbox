ARG BASE_IMAGE=python:3.12-slim

FROM ${BASE_IMAGE} AS base
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=.
ENV UV_LINK_MODE=copy

RUN pip install uv

WORKDIR /code
COPY pyproject.toml uv.lock /code/

RUN uv sync --frozen --no-dev

WORKDIR /code

ENTRYPOINT ["uv", "run", "--no-sync", "python", "lockbox"]

FROM base AS dev
RUN apt-get update && apt-get install -y g++ && uv sync --frozen && apt-get remove -y g++
COPY . /code

FROM base AS final
COPY . /code
