

# Base image: Python 3.13 slim version for a minimal footprint
FROM python:3.13-slim AS builder

# Set working directory for all subsequent commands
WORKDIR /app

# Python environment variables:
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures Python output is sent straight to terminal without buffering
ENV PYTHONUNBUFFERED=1

# Install system dependencies:
# libpq-dev: Required for psycopg2 (PostgreSQL adapter)
# gcc: Required for compiling some Python packages
RUN apt-get update \
    && apt-get -y install libpq-dev gcc pipx git

RUN pipx install hatch

   # Copy the rest of application code to container
COPY . .

# create default environment
RUN pipx run hatch env create default

# Document that the container listens on port 8000
EXPOSE 8000

# Make the entrypoint script executable
RUN chmod +x  /app/entrypoint.sh

# Set the entrypoint script as the default command
# This will run migrations, collect static files, and start Gunicorn
CMD pipx run hatch run ./entrypoint.sh

