@echo off
echo [🔧] Creating virtual environment...
python -m venv venv

echo [📦] Activating virtual environment...
call venv\Scripts\activate

echo [⬇️] Installing dependencies...
pip install -r requirements.txt

echo [🚀] Starting the FlexFit App...
python flex/frontend/flexfit.py

pause