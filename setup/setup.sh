#!/bin/bash
echo "[🔧] Creating virtual environment..."
python3 -m venv venv

echo "[📦] Activating virtual environment..."
source venv/bin/activate

echo "[⬇️] Installing dependencies..."
pip install -r revised_requirements.txt

echo "[🚀] Starting the FlexFit App..."
python3 FlexFit_App-main/frontend/flexfit.py