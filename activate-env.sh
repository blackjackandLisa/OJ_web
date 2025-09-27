#!/bin/bash
# Quick script to activate virtual environment

if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run ./deploy-linux.sh first"
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Virtual environment activated!"
echo "You can now run: python manage.py runserver"

# Keep the shell active with the virtual environment
exec bash
