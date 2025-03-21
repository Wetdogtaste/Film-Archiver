"""
Film Archiver - Configuration Settings
"""
import os
import logging
import sys
from pathlib import Path

# Version information
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_DATE = "2024-02-08"
APP_VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"

# Application Constants
APP_NAME = "Film Archiver"
APP_VERSION = "1.0.0"

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

# Theme Colors
LIGHT_THEME = {
    'bg': '#FFFFFF',
    'fg': '#000000',
    'select_bg': '#0A84FF',
    'select_fg': '#FFFFFF',
    'button': '#F0F0F0',
    'button_active': '#E0E0E0',
    'entry_bg': '#FFFFFF',
    'tooltip_bg': '#FFFFEA',
    'tooltip_fg': '#000000',
    'error': '#FF3B30'
}

DARK_THEME = {
    'bg': '#2D2D2D',
    'fg': '#FFFFFF',
    'select_bg': '#454545',
    'select_fg': '#FFFFFF',
    'button': '#404040',
    'button_active': '#505050',
    'entry_bg': '#383838',
    'tooltip_bg': '#4A4A4A',
    'tooltip_fg': '#FFFFFF',
    'error': '#FF6B6B'
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
