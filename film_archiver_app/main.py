#!/usr/bin/env python3
"""
Film Archiver - Main Entry Point
"""
import sys
import logging
import tkinter as tk
from tkinter import messagebox

from config.settings import configure_logging
from ui.main_window import FilmArchiverWindow

def main():
    """Main application entry point with improved error handling"""
    try:
        # Configure logging
        configure_logging()
        logger = logging.getLogger(__name__)
        
        # Create main window
        root = tk.Tk()
        app = FilmArchiverWindow(root)
        
        # Set up window close handling
        def on_closing():
            try:
                root.destroy()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
                
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        logging.critical(f"Fatal error: {e}", exc_info=True)
        messagebox.showerror(
            "Fatal Error",
            "An unexpected error occurred. Please check the log file for details."
        )
        sys.exit(1)

if __name__ == "__main__":
    main()