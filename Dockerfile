FROM python:3.9-alpine3.13
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
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .temp-build-deps \
        build-base postgresql-dev musl-dev  zlib zlib-dev openssl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .temp-build-deps && \
    adduser -D -H collabus-user &&\
    mkdir -p /vo/web/media && \
    mkdir -p /vol/web/static && \
    chown -R collabus-user:collabus-user /vol &&\
    chmod -R 755 /vol

ENV PATH="/py/bin:$PATH"

USER collabus-user