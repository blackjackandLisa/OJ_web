@echo off
REM Quick script to activate virtual environment

if not exist venv (
    echo Virtual environment not found!
    echo Please run setup-dev.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Virtual environment activated!
echo You can now run: python manage.py runserver
cmd /k
