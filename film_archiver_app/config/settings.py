"""
Film Archiver - Configuration Settings

A tool for organizing and renaming film photography scans with metadata support.

Author: Michael Ziebell
GitHub: https://github.com/Wetdogtaste
Copyright: 2024-2025 Michael Ziebell
"""
import os
import logging
import sys
from pathlib import Path

__author__ = "Michael Ziebell"
__copyright__ = "Copyright 2024-2025, Michael Ziebell"
__license__ = "MIT"

# Version information
VERSION_MAJOR = 1
VERSION_MINOR = 2
VERSION_PATCH = 4
VERSION_DATE = "2025-12-03"
APP_VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"

# Application Constants
APP_NAME = "Film Archiver"
APP_VERSION = "1.2.4"

# Platform-specific settings
IS_MACOS = sys.platform == 'darwin'

# Directory Settings
if IS_MACOS:
    APP_DIR = Path.home() / "Library/Application Support/FilmArchiver"
    CACHE_DIR = Path.home() / "Library/Caches/FilmArchiver"
    LOG_DIR = Path.home() / "Library/Logs/FilmArchiver"
else:
    APP_DIR = Path.home() / ".filmarchiver"
    CACHE_DIR = APP_DIR / "cache"
    LOG_DIR = APP_DIR / "logs"

# Create necessary directories
for directory in [APP_DIR, CACHE_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File Settings
SUPPORTED_FORMATS = {
    # Common Image Formats
    '.jpg': 'JPEG Image',
    '.jpeg': 'JPEG Image',
    '.png': 'PNG Image',
    '.tiff': 'TIFF Image',
    '.tif': 'TIFF Image',
    '.bmp': 'Bitmap Image',
    
    # RAW Formats
    '.cr2': 'Canon RAW',
    '.cr3': 'Canon CR3 RAW',
    '.crw': 'Canon RAW',
    '.nef': 'Nikon RAW',
    '.arw': 'Sony RAW',
    '.raw': 'RAW Image',
    '.raf': 'Fujifilm RAW',
    '.dng': 'Digital Negative',
    
    # High Efficiency Formats
    '.heif': 'HEIF Image',
    '.heic': 'HEIC Image',
    
    # Professional Formats
    '.psd': 'Photoshop Document',
    '.xcf': 'GIMP Image',
    
    # Additional Formats
    '.webp': 'WebP Image',
    '.jxr': 'JPEG XR',
    '.j2k': 'JPEG 2000'
}

# UI Settings
MAX_THUMBNAIL_SIZE = (300, 300)
MAX_CACHE_ENTRIES = 50
THUMBNAIL_QUALITY = 85

# Theme Colors - macOS Finder-matching styles
LIGHT_THEME = {
    'bg': '#ECECEC',           # macOS light mode window background
    'fg': '#000000',           # Black text
    'select_bg': '#0A84FF',    # macOS blue selection
    'select_fg': '#FFFFFF',    # White text on selection
    'button': '#FFFFFF',       # White button background
    'button_active': '#E5E5E5',# Slightly darker on hover
    'entry_bg': '#FFFFFF',     # White entry background
    'list_bg': '#FFFFFF',      # White list background
    'list_row_bg': '#FFFFFF',  # List row background
    'tooltip_bg': '#FFFFEA',
    'tooltip_fg': '#000000',
    'error': '#FF3B30',
    'border': '#C8C8C8',       # Light border color
}

DARK_THEME = {
    'bg': '#2D2D2D',           # macOS dark mode window background (Finder sidebar)
    'fg': '#FFFFFF',           # White text
    'select_bg': '#0A84FF',    # macOS blue selection (same as light theme)
    'select_fg': '#FFFFFF',    # White text on selection
    'button': '#3A3A3A',       # Dark button background
    'button_active': '#4A4A4A',# Slightly lighter on hover
    'entry_bg': '#1E1E1E',     # Dark entry background (matches Finder list rows)
    'list_bg': '#1E1E1E',      # Dark list background (Finder file list)
    'list_row_bg': '#2D2D2D',  # Alternating row color
    'tooltip_bg': '#3A3A3A',
    'tooltip_fg': '#FFFFFF',
    'error': '#FF453A',        # macOS red error
    'border': '#3D3D3D',       # Dark border color
}

def configure_logging():
    """Configure application logging"""
    log_file = LOG_DIR / f"{APP_NAME.lower()}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Set third-party loggers to WARNING level
    logging.getLogger('PIL').setLevel(logging.WARNING)
