# Use an official Python image as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies for building Python packages and uv
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libpq-dev \
    make \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy Makefile and project configuration files
COPY Makefile pyproject.toml uv.lock /app/

# Run Makefile to set up the environment
RUN make setup install

# Copy the rest of the application code
COPY . /app/

# Expose port 8000 for the Django app
EXPOSE 8000

# Default command to run the application
CMD ["make", "run"]
