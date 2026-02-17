#!/bin/bash

# Run Music Recommendation System Backend

echo "Starting Music Recommendation System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the server
echo "Starting server on http://localhost:8001"
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
