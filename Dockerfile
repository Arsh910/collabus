FROM python:3.9-slim
LABEL maintanier="collabus"

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false 

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        libjpeg-dev \
        gfortran \
        build-essential \
        libpq-dev \
        zlib1g-dev \
        libssl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt ; fi && \
    rm -rf /var/lib/apt/lists/* /tmp && \
    useradd -m -d /nonexistent -s /usr/sbin/nologin collabus-user && \
    mkdir -p /vol/web/media /vol/web/static && \
    chown -R collabus-user:collabus-user /vol && \
    chmod -R 755 /vol

ENV PATH="/py/bin:$PATH"

USER collabus-user