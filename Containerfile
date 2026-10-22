

# Use a Python image with uv pre-installed
FROM codeberg.org/margau/buildenv-uv:0.13.5@sha256:ef304ce0bcf2f62a497bb2a120e7b5d82e00ec6be6ea3bb378fbb6b5251049c0

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

RUN apk add tzdata

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=/app/uv.lock \
    --mount=type=bind,source=pyproject.toml,target=/app/pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Make the entrypoint script executable
RUN chmod +x  /app/entrypoint.sh

# Set the entrypoint script as the default command
# This will run migrations, collect static files, and start Gunicorn
CMD ["/app/entrypoint.sh"]

