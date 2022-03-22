ARG PYTHON_VERSION=3.10
ARG SOURCE_DIR=rarible_marketplace_indexer
ARG POETRY_PATH=/opt/poetry
ARG VENV_PATH=/opt/venv
ARG APP_PATH=/opt/app
ARG APP_USER=dipdup

FROM python:${PYTHON_VERSION}-slim-buster as runtime-base

ARG VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

ARG APP_PATH
WORKDIR $APP_PATH

ARG APP_USER
RUN useradd -ms /bin/bash $APP_USER

FROM python:${PYTHON_VERSION}-slim-buster as builder-base

ARG VENV_PATH
ARG POETRY_PATH
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PATH="$POETRY_PATH/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update \
 && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential \
        git \
    \
    # install poetry
 && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - \
 && mv $HOME/.poetry $POETRY_PATH \
 && poetry --version \
    \
    # configure poetry & make a virtualenv ahead of time since we only need one
 && python -m venv $VENV_PATH \
 && poetry config virtualenvs.create false \
    \
    # cleanup
 && rm -rf /var/lib/apt/lists/*

FROM builder-base as builder-production

COPY ["poetry.lock", "pyproject.toml", "./"]

RUN poetry install --no-dev --no-interaction --no-ansi -vvv

FROM runtime-base as runtime

ARG VENV_PATH
COPY --from=builder-production ["$VENV_PATH", "$VENV_PATH"]

ARG APP_USER
USER $APP_USER

ARG SOURCE_DIR
COPY --chown=$APP_USER $SOURCE_DIR ./$SOURCE_DIR
COPY --chown=$APP_USER dipdup*.yml ./

ENTRYPOINT ["dipdup"]
CMD ["run"]
