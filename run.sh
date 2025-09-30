#!/bin/bash

# Iranian Product Search Engine - Quick Start Script

echo "🛒 Iranian Product Search Engine"
echo "================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is required but not installed."
    exit 1
fi

echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🚀 Starting the application..."
    echo "   Open your browser and go to: http://localhost:8501"
    echo ""
    streamlit run app.py
else
    echo "❌ Failed to install dependencies. Please check the error messages above."
    exit 1
fi