#!/bin/bash

# Create necessary directories
mkdir -p icon.iconset

# Convert SVG to PNG at different sizes
for size in 16 32 64 128 256 512; do
    magick icon.svg -resize ${size}x${size} icon.iconset/icon_${size}x${size}.png
    magick icon.svg -resize $((size*2))x$((size*2)) icon.iconset/icon_${size}x${size}@2x.png
done

# Create icns file
iconutil -c icns icon.iconset

# Clean up
rm -rf icon.iconset
