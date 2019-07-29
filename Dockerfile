FROM python:3.7-slim
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ARG REQS=--no-dev

RUN apt-get update && apt-get install -y curl

ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN echo 'export PATH=$PATH:/root/.poetry/bin' >> /root/.bashrc
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
RUN pip install -U pip

WORKDIR /code
COPY . /code

RUN /bin/bash -c "/root/.poetry/bin/poetry install ${REQS}"
RUN python setup.py install

ENTRYPOINT ["lockbox"]
