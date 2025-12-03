#!/bin/bash

# Film Archiver - GitHub Release Script
# This script creates a new GitHub release and uploads the DMG file
#
# Prerequisites:
#   - GitHub CLI (gh) must be installed: brew install gh
#   - You must be authenticated: gh auth login
#
# Usage: ./create_github_release.sh

set -e

# Configuration
VERSION="1.2.4"
DMG_FILE="Film_Archiver_v${VERSION}.dmg"
REPO="Wetdogtaste/Film-Archiver"
TAG="v${VERSION}"
RELEASE_TITLE="Film Archiver v${VERSION}"

# Release notes (can be customized for each release)
RELEASE_NOTES="## Film Archiver v${VERSION}

### What's New
- Updated Film Archiver Manual with latest documentation

### Installation
1. Download \`${DMG_FILE}\` below
2. Open the DMG file
3. Drag Film Archiver to your Applications folder
4. Launch from Applications or Launchpad

### Requirements
- macOS 10.13 (High Sierra) or later
- Apple Silicon (ARM64) or Intel Mac

### Checksums
Run \`shasum -a 256 ${DMG_FILE}\` to verify the download integrity.
"

echo "Film Archiver GitHub Release Script"
echo "===================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Install it with: brew install gh"
    echo "Then authenticate with: gh auth login"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub CLI."
    echo "Run: gh auth login"
    exit 1
fi

# Check if DMG file exists
if [ ! -f "${DMG_FILE}" ]; then
    echo "Error: DMG file not found: ${DMG_FILE}"
    echo "Please run ./build_dmg.sh and ./create_dmg.sh first."
    exit 1
fi

# Calculate checksum
echo "Calculating SHA-256 checksum..."
CHECKSUM=$(shasum -a 256 "${DMG_FILE}" | awk '{print $1}')
echo "Checksum: ${CHECKSUM}"

# Add checksum to release notes
RELEASE_NOTES="${RELEASE_NOTES}
\`\`\`
SHA-256: ${CHECKSUM}
\`\`\`

---
*Built on $(date '+%Y-%m-%d')*"

echo ""
echo "Creating release ${TAG}..."
echo "Repository: ${REPO}"
echo "DMG File: ${DMG_FILE}"
echo ""

# Check if release already exists
if gh release view "${TAG}" --repo "${REPO}" &> /dev/null; then
    echo "Warning: Release ${TAG} already exists."
    read -p "Do you want to delete it and create a new one? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Deleting existing release..."
        gh release delete "${TAG}" --repo "${REPO}" --yes
        # Also delete the tag if it exists
        git push origin --delete "${TAG}" 2>/dev/null || true
    else
        echo "Aborted."
        exit 1
    fi
fi

# Create the release with the DMG file
echo "Creating GitHub release..."
gh release create "${TAG}" \
    --repo "${REPO}" \
    --title "${RELEASE_TITLE}" \
    --notes "${RELEASE_NOTES}" \
    --latest \
    "${DMG_FILE}"

echo ""
echo "============================================"
echo "Release created successfully!"
echo "============================================"
echo ""
echo "Release URL: https://github.com/${REPO}/releases/tag/${TAG}"
echo ""
echo "The release is now live and marked as 'latest'."
echo ""
