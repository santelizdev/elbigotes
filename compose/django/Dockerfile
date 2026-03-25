FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# PostGIS support requires GEOS, GDAL and PROJ system libraries inside the container.
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        binutils \
        gdal-bin \
        gcc \
        libgdal-dev \
        libgeos-dev \
        libproj-dev \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements /tmp/requirements
RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements/dev.txt

COPY . /app

RUN chmod +x /app/scripts/*.sh
