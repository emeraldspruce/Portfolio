#!/bin/bash

# Exit on any error
set -e

# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip (optional but recommended)
pip install --upgrade pip

# Install Flask
pip install flask

# Deactivate the virtual environment
deactivate

echo "✅ Flask installed in virtual environment 'venv'."
echo "👉 To activate it later, run: source venv/bin/activate"
