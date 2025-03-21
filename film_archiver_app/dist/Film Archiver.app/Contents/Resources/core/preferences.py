"""
Film Archiver - Preferences Manager
"""
import os
import json
import logging
from config.settings import APP_DIR

logger = logging.getLogger(__name__)

class PreferenceManager:
    def __init__(self):
        self.cameras = []
        self.films = []
        self.preferences_file = APP_DIR / "preferences.json"
        self.load_preferences()
    
    def load_preferences(self):
        """Load saved preferences from file"""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r') as f:
                    prefs = json.load(f)
                    self.cameras = prefs.get('cameras', [])
                    self.films = prefs.get('films', [])
        except Exception as e:
            logger.error(f"Error loading preferences: {e}")
    
    def save_preferences(self):
        """Save current preferences to file"""
        try:
            os.makedirs(os.path.dirname(self.preferences_file), exist_ok=True)
            with open(self.preferences_file, 'w') as f:
                json.dump({
                    'cameras': self.cameras,
                    'films': self.films
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")
    
    def get_cameras(self):
        """Get list of saved cameras"""
        return sorted(self.cameras)
    
    def get_films(self):
        """Get list of saved films"""
        return sorted(self.films)
    
    def add_camera(self, camera):
        """Add a camera to saved list"""
        camera = camera.strip().upper()
        if camera and camera not in self.cameras:
            self.cameras.append(camera)
            self.save_preferences()
    
    def add_film(self, film):
        """Add a film to saved list"""
        film = film.strip().upper()
        if film and film not in self.films:
            self.films.append(film)
            self.save_preferences()
    
    def remove_camera(self, camera):
        """Remove a camera from saved list"""
        camera = camera.strip().upper()
        if camera in self.cameras:
            self.cameras.remove(camera)
            self.save_preferences()
    
    def remove_film(self, film):
        """Remove a film from saved list"""
        film = film.strip().upper()
        if film in self.films:
            self.films.remove(film)
            self.save_preferences()