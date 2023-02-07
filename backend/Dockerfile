# pull the official docker image
FROM python:3.11.1-slim

# set work directory
WORKDIR /backend

# install dependencies
COPY poetry.lock .
COPY pyproject.toml .

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

# copy project
COPY . .
