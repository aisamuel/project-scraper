# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=your_project.settings.production \
    DEBUG=0 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y netcat-openbsd

RUN pip install --upgrade pip

# Copy requirements file and install dependencies
COPY server/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project
COPY server /app/

# Copy entrypoint script & set permissions
COPY server/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=product_scraper.settings

# Expose the port that Django runs on
EXPOSE 8000

# Run entrypoint script
ENTRYPOINT ["/entrypoint.sh"]