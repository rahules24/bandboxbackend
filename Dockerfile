ARG PYTHON_VERSION=3.12-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install psycopg2 dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# set work directory
WORKDIR /code

# install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

# copy project code
COPY . /code

# copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# expose port
EXPOSE 8000

# set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# start Gunicorn server
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "bbdBackend.wsgi"]
