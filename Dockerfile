FROM python:3.7.1-alpine as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev make

RUN pip3 install nltk
RUN pip3 install psycopg2-binary
RUN python -m nltk.downloader punkt words averaged_perceptron_tagger maxent_ne_chunker

###############################################
# Builder Image
###############################################
FROM python-base as builder-base

ENV POETRY_VERSION=1.1.0

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN apk add libressl-dev \
    libffi-dev
RUN pip3 install pynacl 
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN pip install cryptography==3.4.6 
RUN pip3 install setuptools_rust docker-compose
RUN pip3 install --no-cache-dir poetry==${POETRY_VERSION} && \
    apk del \
    curl \
    gcc \
    libressl-dev \
    libffi-dev
RUN apk add automake g++ subversion
RUN apk add krb5-libs

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev

###############################################
# Production Image
###############################################
FROM python-base as production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY ./ /src/

WORKDIR /src/

EXPOSE 8000

CMD ["gunicorn", "IsItFake.wsgi:application", "--host", "0.0.0.0", "--port", "8000"]
