#!/bin/bash
# run.sh - Run the Hadith application

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install PyQt6 rapidfuzz
else
    source venv/bin/activate
fi

# Run the application
python src/main.py