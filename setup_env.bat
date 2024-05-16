@echo off
REM Ensure any existing virtual environment is deleted
if exist env rd /s /q env

REM Create a new virtual environment
python -m venv env

REM Check if the virtual environment was created successfully
if not exist env\Scripts\activate (
    echo Failed to create virtual environment. Ensure Python is installed and added to PATH.
    exit /b 1
)

REM Activate the virtual environment
call env\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Clear pip cache
pip cache purge

REM Install required packages from requirements.txt
pip install -r requirements.txt

echo Virtual environment setup complete.
pause
