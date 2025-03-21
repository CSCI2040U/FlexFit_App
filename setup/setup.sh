#!/bin/bash

echo "🌱 Setting up FlexFit App on Linux/macOS..."

# Step 1: Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Step 2: Upgrade pip
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Step 3: Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete. You can now run your app!"
