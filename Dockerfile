# Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

# copy uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

WORKDIR /app

# Install the Python dependencies
RUN uv sync --frozen --no-cache
RUN uv pip install -e .

# Expose the port that the application will run on
EXPOSE 8000

# Command to run the application
CMD ["/app/.venv/bin/apisk", "-P", "8000"]
