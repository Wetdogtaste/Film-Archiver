#!/usr/bin/env python3
"""
Film Archiver - Main Entry Point

Critical: The root Tk window MUST be created before any other tkinter-dependent
modules are imported to prevent phantom/blank Tk windows from appearing.
"""
import sys
import os

# Set environment variables before any tkinter imports to prevent phantom windows
os.environ['TK_SILENCE_DEPRECATION'] = '1'

def _is_bundled():
    """Check if we're running as a bundled application."""
    return getattr(sys, 'frozen', False)

def _get_bundle_dir():
    """Get the base directory for the bundled application."""
    if _is_bundled():
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def _get_tkdnd_platform():
    """Get the platform-specific tkdnd subdirectory name."""
    import platform
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == 'darwin':
        # macOS - detect ARM vs Intel
        if machine in ('arm64', 'aarch64'):
            return 'osx-arm64'
        else:
            return 'osx-x64'
    elif system == 'windows':
        if machine in ('amd64', 'x86_64'):
            return 'win-x64'
        elif machine in ('arm64', 'aarch64'):
            return 'win-arm64'
        else:
            return 'win-x86'
    else:  # Linux
        if machine in ('amd64', 'x86_64'):
            return 'linux-x64'
        else:
            return 'linux-arm64'

def _setup_bundled_paths():
    """Set up paths for the bundled application."""
    if not _is_bundled():
        return
    
    bundle_dir = _get_bundle_dir()
    
    # Add bundle directory to Python path for module imports
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)
    
    # Determine the correct platform directory for tkdnd
    platform_dir = _get_tkdnd_platform()
    
    # Set up tkdnd library path for tkinterdnd2
    # Must point to the platform-specific directory
    tkdnd_paths = [
        os.path.join(bundle_dir, 'tkinterdnd2', 'tkdnd', platform_dir),
        os.path.join(bundle_dir, 'tkdnd', platform_dir),
        os.path.join(bundle_dir, 'tkinterdnd2', 'tkdnd'),
        os.path.join(bundle_dir, 'tkdnd'),
    ]
    
    for tkdnd_path in tkdnd_paths:
        if os.path.exists(tkdnd_path):
            os.environ['TKDND_LIBRARY'] = tkdnd_path
            # Also set TK_LIBRARY_PATH which some versions use
            os.environ['TK_DND_PATH'] = tkdnd_path
            break

def _setup_tkdnd_tcl_path(root, logger=None):
    """Set up the Tcl auto_path for tkdnd after Tk is initialized."""
    if not _is_bundled():
        return False
    
    bundle_dir = _get_bundle_dir()
    platform_dir = _get_tkdnd_platform()
    
    # The platform-specific directory that contains pkgIndex.tcl and the library
    tkdnd_platform_paths = [
        os.path.join(bundle_dir, 'tkinterdnd2', 'tkdnd', platform_dir),
        os.path.join(bundle_dir, 'tkdnd', platform_dir),
    ]
    
    for tkdnd_path in tkdnd_platform_paths:
        if os.path.exists(tkdnd_path):
            try:
                # Add the platform-specific directory to Tcl's auto_path
                tcl_path = tkdnd_path.replace('\\', '/')
                root.tk.eval(f'lappend auto_path {{{tcl_path}}}')
                if logger:
                    logger.info(f"Added tkdnd path to Tcl auto_path: {tcl_path}")
                return True
            except Exception as e:
                if logger:
                    logger.warning(f"Failed to add tkdnd path: {e}")
    return False

# Set up bundled paths BEFORE any imports
_setup_bundled_paths()

# Import tkinter FIRST - before any other modules that might use it
import tkinter as tk

def _patch_tkinterdnd2_platform():
    """
    Patch tkinterdnd2 to use the correct platform directory in bundled apps.
    This must be called BEFORE importing/using TkinterDnD.
    """
    if not _is_bundled():
        return
    
    try:
        import tkinterdnd2
        
        # Get the correct platform directory
        platform_dir = _get_tkdnd_platform()
        bundle_dir = _get_bundle_dir()
        
        # Find the tkdnd path and set it correctly
        tkdnd_base = os.path.join(bundle_dir, 'tkinterdnd2', 'tkdnd')
        if os.path.exists(tkdnd_base):
            # Set the platform-specific path
            platform_path = os.path.join(tkdnd_base, platform_dir)
            if os.path.exists(platform_path):
                # Monkeypatch tkinterdnd2's internal TkdndVersion to point to correct path
                # Store the correct path for later use
                tkinterdnd2._tkdnd_platform_path = platform_path
                
                # Also try setting module-level variables
                if hasattr(tkinterdnd2, '_tkdnd_path'):
                    tkinterdnd2._tkdnd_path = platform_path
    except Exception as e:
        pass

# Patch tkinterdnd2 platform detection before using it
_patch_tkinterdnd2_platform()

def main():
    """Main application entry point with improved error handling"""
    import logging
    
    # Configure basic logging early
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    if _is_bundled():
        logger.info(f"Running as bundled app from: {_get_bundle_dir()}")
    
    # Create the root window
    root = None
    dnd_enabled = False
    
    # In the bundled app, skip TkinterDnD.Tk() since tkdnd library has compatibility issues
    # This prevents the phantom window from appearing
    if _is_bundled():
        logger.info("Using standard Tk() for bundled app")
        root = tk.Tk()
    else:
        # In development, try TkinterDnD.Tk() for drag-and-drop support
        try:
            from tkinterdnd2 import TkinterDnD
            root = TkinterDnD.Tk()
            dnd_enabled = True
            logger.info("Created TkinterDnD.Tk() window")
        except ImportError as e:
            logger.warning(f"TkinterDnD not available: {e}")
        except Exception as e:
            logger.warning(f"TkinterDnD.Tk() failed: {e}")
        
        # Fall back to standard Tk if TkinterDnD failed
        if root is None:
            logger.info("Falling back to standard Tk()")
            root = tk.Tk()
    
    # Temporarily withdraw the window while we set up everything
    root.withdraw()
    
    # Destroy any phantom Tk windows that might have been created
    try:
        for widget in root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
    except:
        pass
    
    try:
        # Import configuration after basic setup
        from config.settings import configure_logging
        
        # Configure full logging
        configure_logging()
        logger = logging.getLogger(__name__)
        logger.info("Film Archiver starting...")
        
        # Import the main window module AFTER root is created
        # This prevents tkcalendar and other modules from creating phantom windows
        from ui.main_window import FilmArchiverWindow
        
        # Create the application
        app = FilmArchiverWindow(root)
        
        # Create a proper menu bar with standard macOS menu items
        # This replaces the default menu bar which includes the unwanted "Run widget demo" item
        import platform
        from config.settings import APP_NAME, APP_VERSION
        
        def create_menu_bar():
            menubar = tk.Menu(root)
            
            if platform.system() == 'Darwin':
                # macOS specific menus
                
                # Application menu (automatically named after the app in bundled builds)
                app_menu = tk.Menu(menubar, name='apple', tearoff=0)
                menubar.add_cascade(menu=app_menu)
                
                # About menu item
                def show_about():
                    from tkinter import messagebox
                    messagebox.showinfo(
                        f"About {APP_NAME}",
                        f"{APP_NAME}\n\n"
                        f"Version: {APP_VERSION}\n\n"
                        f"A tool for organizing and archiving\n"
                        f"film photography scans with proper\n"
                        f"naming, dates, and EXIF metadata.\n\n"
                        f"© 2024"
                    )
                
                app_menu.add_command(label=f"About {APP_NAME}", command=show_about)
                app_menu.add_separator()
                
                # Preferences (placeholder for future use)
                # app_menu.add_command(label="Preferences...", command=lambda: None, accelerator="⌘,")
                # app_menu.add_separator()
                
                # Quit is automatically added by macOS for the apple menu
                
                # Help menu
                help_menu = tk.Menu(menubar, name='help', tearoff=0)
                menubar.add_cascade(label="Help", menu=help_menu)
                
                def show_help():
                    import webbrowser
                    webbrowser.open("https://github.com/Wetdogtaste/Film-Archiver")
                
                help_menu.add_command(label=f"{APP_NAME} Help", command=show_help)
                
            else:
                # Non-macOS menu bar (Windows/Linux)
                
                # File menu
                file_menu = tk.Menu(menubar, tearoff=0)
                menubar.add_cascade(label="File", menu=file_menu)
                file_menu.add_command(label="Exit", command=root.quit)
                
                # Help menu
                help_menu = tk.Menu(menubar, tearoff=0)
                menubar.add_cascade(label="Help", menu=help_menu)
                
                def show_about():
                    from tkinter import messagebox
                    messagebox.showinfo(
                        f"About {APP_NAME}",
                        f"{APP_NAME} v{APP_VERSION}\n\n"
                        f"A tool for organizing film photography scans."
                    )
                
                help_menu.add_command(label="About", command=show_about)
            
            root.config(menu=menubar)
            logger.info("Created custom menu bar")
        
        create_menu_bar()
        
        # Set up window close handling
        def on_closing():
            try:
                root.destroy()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
                
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Now show the window
        root.deiconify()
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        logging.critical(f"Fatal error: {e}", exc_info=True)
        # Use the existing root for the error message
        try:
            from tkinter import messagebox
            root.deiconify()  # Make sure window is visible
            messagebox.showerror(
                "Fatal Error",
                f"An unexpected error occurred:\n{str(e)}\n\nPlease check the log file for details."
            )
        except:
            pass  # Fail silently if messagebox can't be shown
        finally:
            try:
                root.destroy()
            except:
                pass
        sys.exit(1)

if __name__ == "__main__":
    main()
