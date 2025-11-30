#!/usr/bin/env python3
"""
Film Archiver - Main Entry Point
"""
import sys
import logging
import tkinter as tk

# Try to import TkinterDnD for drag and drop support
try:
    from tkinterdnd2 import TkinterDnD
    USE_DND = True
except ImportError:
    USE_DND = False

from config.settings import configure_logging
from ui.main_window import FilmArchiverWindow

def main():
    """Main application entry point with improved error handling"""
    try:
        # Configure logging
        configure_logging()
        logger = logging.getLogger(__name__)
        
        # Create main window with drag and drop support if available
        dnd_enabled = False
        if USE_DND:
            try:
                root = TkinterDnD.Tk()
                dnd_enabled = True
                logger.info("TkinterDnD initialized - drag and drop enabled")
            except RuntimeError as e:
                # tkdnd native library not found - fall back to regular Tk
                logger.warning(f"TkinterDnD failed to initialize ({e}) - falling back to standard Tk")
                root = tk.Tk()
        else:
            root = tk.Tk()
            logger.info("TkinterDnD not installed - drag and drop disabled")
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
        # Lazy import messagebox to prevent creating phantom Tk windows
        from tkinter import messagebox
        try:
            messagebox.showerror(
                "Fatal Error",
                "An unexpected error occurred. Please check the log file for details."
            )
        except:
            pass  # Fail silently if messagebox can't be shown
        sys.exit(1)

if __name__ == "__main__":
    main()
