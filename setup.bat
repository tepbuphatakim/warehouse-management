@echo off
REM Step 1: Create a virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    exit /b 1
)

REM Step 2: Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

REM Step 3: Install dependencies from requirements.txt
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    exit /b 1
)

echo Virtual environment setup completed successfully!
pause
