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
VERSION="1.2.1"
DMG_NAME="Film_Archiver_v${VERSION}.dmg"
VOLUME_NAME="Film Archiver"

echo "Creating DMG file: ${DMG_NAME}"

# Activate virtual environment if it exists (for Python script)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create DMG background image
echo "Creating DMG background image..."
python3 create_dmg_background.py

# Check if background was created
if [ ! -f "dmg_background.png" ]; then
    echo "Warning: Could not create background image, proceeding without it"
fi

# Create a temporary directory for DMG contents
TEMP_DIR=$(mktemp -d)
echo "Using temporary directory: ${TEMP_DIR}"

# Copy the application to the temporary directory
echo "Copying application..."
cp -R "dist/Film Archiver.app" "${TEMP_DIR}/"

# Create a symbolic link to /Applications
echo "Creating Applications symlink..."
ln -s /Applications "${TEMP_DIR}/Applications"

# Create .background directory and copy background image
if [ -f "dmg_background.png" ]; then
    mkdir -p "${TEMP_DIR}/.background"
    cp "dmg_background.png" "${TEMP_DIR}/.background/background.png"
fi

# Remove old DMG if it exists
rm -f "${DMG_NAME}"
rm -f "temp_${DMG_NAME}"

# Create a temporary read-write DMG
echo "Creating temporary DMG..."
hdiutil create -volname "${VOLUME_NAME}" \
    -srcfolder "${TEMP_DIR}" \
    -ov -format UDRW \
    "temp_${DMG_NAME}"

# Mount the temporary DMG
echo "Mounting DMG for customization..."
hdiutil attach -readwrite -noverify "temp_${DMG_NAME}"

# Wait for mount
sleep 2

# Use the known mount point
MOUNT_DIR="/Volumes/${VOLUME_NAME}"

echo "Mounted at: ${MOUNT_DIR}"

# Verify mount
if [ ! -d "${MOUNT_DIR}" ]; then
    echo "Error: Mount point not found at ${MOUNT_DIR}"
    echo "Checking /Volumes..."
    ls -la /Volumes/
    exit 1
fi

# Wait for disk to be ready
sleep 2

# Apply Finder customizations using AppleScript
echo "Applying Finder customizations..."
osascript << EOF
tell application "Finder"
    tell disk "${VOLUME_NAME}"
        -- Open the window
        open
        
        -- Set window properties
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set bounds of container window to {100, 100, 760, 500}
        
        -- Set icon view options
        set theViewOptions to icon view options of container window
        set arrangement of theViewOptions to not arranged
        set icon size of theViewOptions to 100
        set text size of theViewOptions to 12
        
        -- Set background (if background image exists)
        try
            set background picture of theViewOptions to file ".background:background.png"
        end try
        
        -- Position the icons
        -- App on the left side
        set position of item "Film Archiver.app" of container window to {165, 180}
        
        -- Applications alias on the right side  
        set position of item "Applications" of container window to {495, 180}
        
        -- Refresh and close
        update without registering applications
        delay 1
        close
    end tell
end tell
EOF

# Sync and wait
sync
sleep 2

# Unmount the DMG
echo "Unmounting DMG..."
hdiutil detach "${MOUNT_DIR}" -force

# Convert to compressed read-only DMG
echo "Converting to compressed DMG..."
hdiutil convert "temp_${DMG_NAME}" \
    -format UDZO \
    -imagekey zlib-level=9 \
    -o "${DMG_NAME}"

# Clean up
echo "Cleaning up..."
rm -f "temp_${DMG_NAME}"
rm -rf "${TEMP_DIR}"

# Verify the DMG
echo "Verifying DMG..."
hdiutil verify "${DMG_NAME}"

echo ""
echo "============================================"
echo "DMG file created successfully: ${DMG_NAME}"
echo "============================================"
echo ""
echo "The DMG includes:"
echo "  - Film Archiver.app"
echo "  - Applications folder shortcut"
echo "  - Visual drag-to-Applications instruction"
echo ""
echo "Done!"
