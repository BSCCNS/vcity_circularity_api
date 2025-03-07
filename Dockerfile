# Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

# copy uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the requirements file into the container
COPY uv.lock .
COPY pyproject.toml .

# Copy the rest of the application code into the container
COPY src/ .

# Install the Python dependencies
RUN uv sync --frozen
RUN uv pip install -e .

# Expose the port that the application will run on
EXPOSE 8000

# Command to run the application
CMD ["apisk","-P", "8000"]
