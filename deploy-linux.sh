#!/bin/bash
# Django OJ System - Linux Server Deployment Script

set -e  # Exit on any error

echo "🚀 Starting Django OJ System deployment on Linux..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.8+ is installed
print_status "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

print_status "Python $PYTHON_VERSION detected ✓"

# Create virtual environment
print_status "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Removing old environment..."
    rm -rf venv
fi

python3 -m venv venv
print_status "Virtual environment created ✓"

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements-linux.txt" ]; then
    pip install -r requirements-linux.txt
    print_status "Linux-specific requirements installed ✓"
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Standard requirements installed ✓"
else
    print_error "No requirements file found!"
    exit 1
fi

# Install additional production dependencies
print_status "Installing production dependencies..."
pip install gunicorn whitenoise

# Database setup
print_status "Setting up database..."
python manage.py migrate
print_status "Database migrations completed ✓"

# Create superuser (optional)
print_status "Creating superuser (optional)..."
echo "Do you want to create a superuser? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    python manage.py createsuperuser
fi

# Create default templates
print_status "Creating default code templates..."
python manage.py create_default_templates
print_status "Default templates created ✓"

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput
print_status "Static files collected ✓"

# Set up judge directories
print_status "Setting up judge system directories..."
mkdir -p sandbox_tmp
mkdir -p judge_temp
mkdir -p media/avatars
chmod 755 sandbox_tmp judge_temp media/avatars
print_status "Judge directories created ✓"

# Create systemd service file
print_status "Creating systemd service file..."
cat > django-oj.service << EOF
[Unit]
Description=Django OJ System
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/gunicorn oj_system.wsgi:application --bind 127.0.0.1:8000 --workers 3
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_status "Systemd service file created: django-oj.service"
print_warning "Copy this file to /etc/systemd/system/ and run:"
print_warning "sudo systemctl daemon-reload"
print_warning "sudo systemctl enable django-oj"
print_warning "sudo systemctl start django-oj"

# Create Nginx configuration
print_status "Creating Nginx configuration..."
cat > nginx-django-oj.conf << EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain
    
    client_max_body_size 20M;
    
    location /static/ {
        alias $(pwd)/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
    
    location /media/ {
        alias $(pwd)/media/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

print_status "Nginx configuration created: nginx-django-oj.conf"
print_warning "Copy this file to /etc/nginx/sites-available/ and create symlink to sites-enabled/"

# Create environment variables template
print_status "Creating environment variables template..."
cat > .env.example << EOF
# Django OJ System Environment Variables
# Copy this file to .env and fill in your values

# Security
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (PostgreSQL example)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=django_oj
# DB_USER=oj_user
# DB_PASSWORD=your_db_password
# DB_HOST=localhost
# DB_PORT=5432

# Email configuration
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-email-password

# Judge system
JUDGE_ENGINE=process
JUDGE_SANDBOX_DIR=sandbox_tmp
JUDGE_DEFAULT_TIME_LIMIT=1000
JUDGE_DEFAULT_MEMORY_LIMIT=256

# Static and media files
STATIC_ROOT=$(pwd)/staticfiles
MEDIA_ROOT=$(pwd)/media
EOF

print_status "Environment template created: .env.example"

print_status "🎉 Deployment completed successfully!"
print_status ""
print_status "Next steps:"
print_status "1. Configure your domain in nginx-django-oj.conf"
print_status "2. Copy django-oj.service to /etc/systemd/system/"
print_status "3. Copy nginx-django-oj.conf to /etc/nginx/sites-available/"
print_status "4. Create .env file from .env.example with your settings"
print_status "5. Start the services:"
print_status "   sudo systemctl start django-oj"
print_status "   sudo systemctl restart nginx"
print_status ""
print_status "Your Django OJ System is ready! 🚀"
