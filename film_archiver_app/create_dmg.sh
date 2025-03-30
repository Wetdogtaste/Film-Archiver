#!/bin/bash

# Exit on error
set -e

echo "Film Archiver DMG Creator"
echo "========================="

# Check if the application exists
if [ ! -d "dist/Film Archiver.app" ]; then
    echo "Error: Application not found at dist/Film Archiver.app"
    echo "Please run ./build_dmg.sh first to build the application."
    exit 1
fi

# Set version
VERSION="1.1.0"
DMG_NAME="Film_Archiver_v${VERSION}.dmg"

echo "Creating DMG file: ${DMG_NAME}"

# Create a temporary directory for DMG contents
TEMP_DIR=$(mktemp -d)
echo "Using temporary directory: ${TEMP_DIR}"

# Copy the application to the temporary directory
echo "Copying application..."
cp -R "dist/Film Archiver.app" "${TEMP_DIR}/"

# Create a symbolic link to /Applications
echo "Creating Applications symlink..."
ln -s /Applications "${TEMP_DIR}/Applications"

# Create the DMG file
echo "Creating DMG file..."
hdiutil create -volname "Film Archiver" \
    -srcfolder "${TEMP_DIR}" \
    -ov -format UDZO \
    "${DMG_NAME}"

# Clean up
echo "Cleaning up..."
rm -rf "${TEMP_DIR}"

echo "DMG file created: ${DMG_NAME}"
echo "Done!"
