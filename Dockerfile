# Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

# set port from env var
ENV API_PORT=${API_PORT:-8000}

# copy uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the rest of the application code into the container
COPY src/ /app

WORKDIR /app

# Copy the requirements file into the container
COPY uv.lock .
COPY pyproject.toml .

# Install the Python dependencies
RUN uv sync --frozen --no-cache
RUN uv pip install -e .

# Expose the port that the application will run on
EXPOSE ${API_PORT}

# Command to run the application
CMD ["/app/.venv/bin/apisk","-P", ${API_PORT}]
