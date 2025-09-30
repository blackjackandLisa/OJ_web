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
RUN apt-get update && apt-get install -y python3-pip && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-linux.txt && \
    rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p sandbox_tmp judge_temp media/avatars staticfiles logs

# Set permissions
RUN chmod -R 755 sandbox_tmp judge_temp media

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🚀 Starting Django OJ System..."\n\
\n\
# Wait for database\n\
echo "⏳ Waiting for database..."\n\
while ! python manage.py shell -c "from django.db import connection; connection.ensure_connection()" 2>/dev/null; do\n\
    echo "⏳ Database not ready, waiting 5 seconds..."\n\
    sleep 5\n\
done\n\
echo "✅ Database connected"\n\
\n\
# Run migrations\n\
echo "🔄 Running migrations..."\n\
python manage.py migrate\n\
\n\
# Create default templates\n\
echo "📝 Creating default templates..."\n\
python manage.py create_default_templates\n\
\n\
# Collect static files\n\
echo "📦 Collecting static files..."\n\
python manage.py collectstatic --noinput\n\
\n\
# Start Gunicorn\n\
echo "🚀 Starting Gunicorn..."\n\
exec gunicorn oj_system.wsgi:application \\\n\
    --bind 0.0.0.0:8000 \\\n\
    --workers 3 \\\n\
    --timeout 120 \\\n\
    --keep-alive 2 \\\n\
    --max-requests 1000 \\\n\
    --max-requests-jitter 100 \\\n\
    --preload\n\
' > start.sh && chmod +x start.sh

# Expose port
EXPOSE 8000

# Start command
CMD ["./start.sh"]
