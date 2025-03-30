"""
Test script for lens metadata functionality
"""
import os
import sys
import tempfile
import unittest
from PIL import Image
import piexif
from pathlib import Path

# Add parent directory to path to import from film_archiver_app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.preferences import PreferenceManager

class TestLensMetadata(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create a test image
        self.test_image_path = self.test_dir / "test_image.jpg"
        self.create_test_image(self.test_image_path)
        
        # Create a preferences manager
        self.pref_manager = PreferenceManager()
        
    def tearDown(self):
        # Clean up temporary directory
        self.temp_dir.cleanup()
        
    def create_test_image(self, path):
        """Create a simple test image"""
        img = Image.new('RGB', (100, 100), color='red')
        img.save(path)
        
    def test_lens_preferences(self):
        """Test saving and loading lens preferences"""
        # Add some test lenses
        test_lenses = ["50MM F1.4", "35MM F2", "85MM F1.8"]
        for lens in test_lenses:
            self.pref_manager.add_lens(lens)
            
        # Check that lenses were added
        saved_lenses = self.pref_manager.get_lenses()
        for lens in test_lenses:
            self.assertIn(lens, saved_lenses)
            
        # Remove a lens
        self.pref_manager.remove_lens(test_lenses[0])
        saved_lenses = self.pref_manager.get_lenses()
        self.assertNotIn(test_lenses[0], saved_lenses)
        
    def test_lens_exif(self):
        """Test adding lens metadata to EXIF"""
        # Create a copy of the test image
        output_path = self.test_dir / "output_image.jpg"
        with open(self.test_image_path, 'rb') as src_file:
            with open(output_path, 'wb') as dst_file:
                dst_file.write(src_file.read())
        
        # Add lens metadata to EXIF
        test_lens = "50MM F1.4"
        try:
            exif_dict = piexif.load(str(output_path))
            exif_dict['Exif'][piexif.ExifIFD.LensModel] = test_lens.encode()
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, str(output_path))
        except Exception as e:
            self.fail(f"Failed to add lens metadata to EXIF: {e}")
            
        # Verify lens metadata in EXIF
        try:
            exif_dict = piexif.load(str(output_path))
            lens_model = exif_dict['Exif'][piexif.ExifIFD.LensModel].decode()
            self.assertEqual(lens_model, test_lens)
        except Exception as e:
            self.fail(f"Failed to read lens metadata from EXIF: {e}")
            
if __name__ == '__main__':
    unittest.main()
