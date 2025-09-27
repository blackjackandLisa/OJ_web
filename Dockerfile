# Django OJ System Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-jdk \
    nodejs \
    npm \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-linux.txt .
RUN pip install --no-cache-dir -r requirements-linux.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p sandbox_tmp judge_temp media/avatars staticfiles

# Set permissions
RUN chmod -R 755 sandbox_tmp judge_temp media

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
python manage.py migrate\n\
python manage.py create_default_templates\n\
gunicorn oj_system.wsgi:application --bind 0.0.0.0:8000 --workers 3\n\
' > start.sh && chmod +x start.sh

# Start command
CMD ["./start.sh"]
