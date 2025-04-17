#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "antenv" ]; then
    python -m venv antenv
fi

# Activate virtual environment
source antenv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Start the application
gunicorn --bind=0.0.0.0:8000 app:app 