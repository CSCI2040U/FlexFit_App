@echo off
echo 🌱 Setting up FlexFit App on Windows...

:: Step 1: Create virtual environment
python -m venv venv

:: Step 2: Activate virtual environment
call venv\Scripts\activate

:: Step 3: Upgrade pip
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip

:: Step 4: Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

echo ✅ Setup complete. You can now run your app!
pause
