@echo off
REM Django OJ System - Windows Development Setup Script

echo Starting Django OJ System development setup...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python detected

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)

python -m venv venv
echo Virtual environment created

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
    echo Dependencies installed
) else (
    echo ERROR: requirements.txt not found
    pause
    exit /b 1
)

REM Database setup
echo Setting up database...
python manage.py migrate
echo Database setup completed

REM Create default templates
echo Creating default templates...
python manage.py create_default_templates
echo Default templates created

REM Create superuser (optional)
echo.
set /p create_user="Do you want to create a superuser? (y/n): "
if /i "%create_user%"=="y" (
    python manage.py createsuperuser
)

echo.
echo =================================
echo Development environment is ready!
echo =================================
echo.
echo To start development:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Start development server: python manage.py runserver
echo 3. Access the system at: http://localhost:8000
echo.
pause
