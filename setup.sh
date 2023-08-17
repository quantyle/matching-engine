#!/bin/bash

# Create a virtual environment
python3.11 -m venv virtualenv

# Activate the virtual environment
source virtualenv/bin/activate

# Install required packages
pip install -r requirements.txt

echo "Virtual environment setup completed."
