# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=grupoMaster.settings_production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create logs directory and media at root
RUN mkdir -p logs
RUN mkdir -p /media

# Collect static files
RUN python manage.py collectstatic --noinput

# Create a non-root user and set ownership BEFORE switching user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
RUN chown appuser:appuser /media
RUN chmod 755 logs
RUN chmod 755 /media

USER appuser

# Expose port
EXPOSE 8005

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8005", "--workers", "3", "grupoMaster.wsgi:application"] 