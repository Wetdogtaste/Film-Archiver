"""
Film Archiver - File Management Module
"""
import os
import logging
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional
from PIL import Image
from datetime import datetime
from config.settings import SUPPORTED_FORMATS, IS_MACOS

Image.MAX_IMAGE_PIXELS = None  # Allows for very large images

logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def select_files(self) -> List[str]:
        """
        Open file dialog and return selected files with proper macOS handling
        """
        try:
            if IS_MACOS:
                try:
                    # Use native macOS file dialog
                    from Foundation import NSOpenPanel
                    panel = NSOpenPanel.alloc().init()
                except ImportError:
                    # Fallback to regular dialog if PyObjC is not available
                    return list(filedialog.askopenfilenames(
                        title="Select Image Files",
                        filetypes=[
                            ("Image files", " ".join(SUPPORTED_FORMATS.keys())),
                            ("All files", "*.*")
                        ]
                    ))
                panel.setCanChooseFiles_(True)
                panel.setCanChooseDirectories_(False)
                panel.setAllowsMultipleSelection_(True)
                
                # Set allowed file types
                allowed_types = [ext[1:] for ext in SUPPORTED_FORMATS.keys()]
                panel.setAllowedFileTypes_(allowed_types)

                if panel.runModal() == 1:  # NSModalResponseOK
                    return [str(url.path()) for url in panel.URLs()]
                return []
            else:
                # Regular file dialog for other platforms
                files = filedialog.askopenfilenames(
                    title="Select Image Files",
                    filetypes=[
                        ("Image files", " ".join(SUPPORTED_FORMATS.keys())),
                        ("All files", "*.*")
                    ]
                )
                return list(files)

        except Exception as e:
            self.logger.error(f"Error in file selection: {e}")
            return []

    def validate_file(self, file_path: str) -> bool:
        """Validate if file is a supported image file"""
        try:
            if not os.path.exists(file_path):
                return False

            # Check file extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in SUPPORTED_FORMATS:
                return False

            # For RAW files, just check if file exists and has correct extension
            raw_formats = ['.cr2', '.cr3', '.crw', '.nef', '.arw', '.raw', '.raf', '.dng']
            if ext in raw_formats:
                return True

            # For other formats, verify with PIL
            try:
                with Image.open(file_path) as img:
                    img.verify()
                return True
            except:
                return False

        except Exception as e:
            self.logger.debug(f"File validation failed for {file_path}: {e}")
            return False

    def create_thumbnail(self, image_path: str, size=(300, 300)) -> Optional[Image.Image]:
        """Create a thumbnail from an image file"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)
                return img.copy()

        except Exception as e:
            self.logger.error(f"Error creating thumbnail for {image_path}: {e}")
            return None

    def get_image_date(self, image_path: str) -> str:
        """Get the image date from EXIF or file system"""
        try:
            # Get file extension
            ext = os.path.splitext(image_path)[1].lower()
            
            # For RAW files and special formats
            if ext in ['.cr2', '.cr3', '.crw', '.nef', '.arw', '.raw', '.raf', '.dng']:
                try:
                    with Image.open(image_path) as img:
                        if hasattr(img, '_getexif') and img._getexif():
                            exif = img._getexif()
                            # Try different EXIF date fields
                            date_fields = [36867, 36868, 306]  # DateTimeOriginal, DateTimeDigitized, DateTime
                            for field in date_fields:
                                if field in exif:
                                    try:
                                        date_str = exif[field]
                                        dt = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                                        return dt.strftime("%m/%d/%Y")
                                    except ValueError:
                                        continue
                except Exception as raw_error:
                    self.logger.debug(f"Error reading RAW format: {raw_error}")
                    pass

            # For standard formats
            else:
                with Image.open(image_path) as img:
                    if hasattr(img, '_getexif') and img._getexif():
                        exif = img._getexif()
                        # Try different EXIF date fields
                        date_fields = [36867, 36868, 306]  # DateTimeOriginal, DateTimeDigitized, DateTime
                        for field in date_fields:
                            if field in exif:
                                try:
                                    date_str = exif[field]
                                    dt = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                                    return dt.strftime("%m/%d/%Y")
                                except ValueError:
                                    continue

            # Fallback to file modification time
            mod_time = os.path.getmtime(image_path)
            return datetime.fromtimestamp(mod_time).strftime("%m/%d/%Y")

        except Exception as e:
            self.logger.error(f"Error getting image date for {image_path}: {e}")
            return "Unknown"
