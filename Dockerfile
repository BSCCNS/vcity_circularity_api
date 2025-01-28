# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY dist/ .

COPY src/cicloapi/data/users_db_fake.json /app/src/cicloapi/data/
RUN chmod 644 /app/src/cicloapi/data/users_db_fake.json

# Install the Python dependencies
RUN pip install cicloapi-0.1-py3-none-any.whl

# Expose the port that the application will run on
EXPOSE 8000

# Command to run the application
CMD ["cicloapi"]
