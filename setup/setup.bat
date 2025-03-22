@echo off
echo 🌱 Setting up FlexFit App on Windows...

:: Step 1: Create virtual environment
python -m venv venv

:: Step 2: Activate virtual environment
call venv\Scripts\activate

:: Step 3: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Step 4: Installing dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo Setup complete. Stay Fit, Let Others Stay Fit!
pause
