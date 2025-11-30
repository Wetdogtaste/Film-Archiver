#!/bin/bash

# Exit on error
set -e

echo "Film Archiver App Builder"
echo "========================="

# Check if virtual environment exists, if not create one
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "Installing required packages..."
python -m pip install -r requirements.txt

# Install PyInstaller if not already installed
if ! python -m pip show pyinstaller > /dev/null 2>&1; then
    echo "Installing PyInstaller..."
    python -m pip install pyinstaller
fi

# Clean up previous build
echo "Cleaning up previous build..."
rm -rf dist build

# Build the application using PyInstaller
echo "Building application with PyInstaller..."
python -m PyInstaller Film_Archiver.spec

echo "Build complete!"
echo "The application has been built and can be found in the dist directory."
echo ""
echo "To create a DMG file for distribution, run:"
echo "./create_dmg.sh"
echo ""
echo "This will create a DMG file with the application and a link to the Applications folder."
echo "The DMG file will be named Film_Archiver_v1.2.1.dmg and will be ready for distribution."
