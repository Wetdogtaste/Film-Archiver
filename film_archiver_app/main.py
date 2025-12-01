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
        import subprocess
        import webbrowser
        from config.settings import APP_NAME, APP_VERSION
        
        def get_docs_path():
            """Get the path to documentation files (bundled or development)."""
            if _is_bundled():
                # In bundled app, docs are in the Resources folder
                bundle_dir = _get_bundle_dir()
                return bundle_dir
            else:
                # In development, docs are in the parent directory
                return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        def show_readme():
            """Display the README in a scrollable window."""
            docs_path = get_docs_path()
            readme_path = os.path.join(docs_path, 'README.md')
            
            if not os.path.exists(readme_path):
                from tkinter import messagebox
                messagebox.showwarning(
                    "README Not Found",
                    f"Could not find README.md at:\n{readme_path}"
                )
                return
            
            # Read the README content
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Error", f"Could not read README:\n{e}")
                return
            
            # Create a new window
            readme_window = tk.Toplevel(root)
            readme_window.title(f"{APP_NAME} - README")
            readme_window.geometry("800x600")
            readme_window.minsize(600, 400)
            
            # Create a frame for the text and scrollbar
            frame = tk.Frame(readme_window)
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Create scrollbar
            scrollbar = tk.Scrollbar(frame)
            scrollbar.pack(side='right', fill='y')
            
            # Create text widget with markdown-friendly formatting
            text = tk.Text(
                frame,
                wrap='word',
                yscrollcommand=scrollbar.set,
                font=('SF Mono', 12) if platform.system() == 'Darwin' else ('Consolas', 11),
                padx=15,
                pady=15,
                spacing1=2,
                spacing3=2
            )
            text.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=text.yview)
            
            # Configure text tags for basic markdown styling
            text.tag_configure('h1', font=('SF Pro Display', 24, 'bold') if platform.system() == 'Darwin' else ('Arial', 20, 'bold'), spacing1=10, spacing3=5)
            text.tag_configure('h2', font=('SF Pro Display', 18, 'bold') if platform.system() == 'Darwin' else ('Arial', 16, 'bold'), spacing1=8, spacing3=4)
            text.tag_configure('h3', font=('SF Pro Display', 14, 'bold') if platform.system() == 'Darwin' else ('Arial', 13, 'bold'), spacing1=6, spacing3=3)
            text.tag_configure('code', font=('SF Mono', 11) if platform.system() == 'Darwin' else ('Consolas', 10), background='#f0f0f0')
            text.tag_configure('bold', font=('SF Pro Text', 12, 'bold') if platform.system() == 'Darwin' else ('Arial', 11, 'bold'))
            
            # Simple markdown rendering
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    text.insert('end', line[2:] + '\n', 'h1')
                elif line.startswith('## '):
                    text.insert('end', line[3:] + '\n', 'h2')
                elif line.startswith('### '):
                    text.insert('end', line[4:] + '\n', 'h3')
                elif line.startswith('```'):
                    continue  # Skip code fence markers
                elif line.startswith('|'):
                    # Table row - display as-is with code formatting
                    text.insert('end', line + '\n', 'code')
                else:
                    # Handle inline formatting
                    text.insert('end', line + '\n')
            
            # Make text read-only
            text.config(state='disabled')
            
            # Focus the new window
            readme_window.focus_force()
        
        def open_manual():
            """Open the PDF manual in the system's default PDF viewer."""
            docs_path = get_docs_path()
            manual_path = os.path.join(docs_path, 'Film Archiver Manual.pdf')
            
            if not os.path.exists(manual_path):
                from tkinter import messagebox
                messagebox.showwarning(
                    "Manual Not Found",
                    f"Could not find Film Archiver Manual.pdf at:\n{manual_path}"
                )
                return
            
            try:
                if platform.system() == 'Darwin':
                    # macOS - use 'open' command to open in Preview
                    subprocess.run(['open', manual_path], check=True)
                elif platform.system() == 'Windows':
                    os.startfile(manual_path)
                else:
                    # Linux - try xdg-open
                    subprocess.run(['xdg-open', manual_path], check=True)
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Error", f"Could not open manual:\n{e}")
        
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
                
                help_menu.add_command(label="Film Archiver Manual", command=open_manual)
                help_menu.add_command(label="View README", command=show_readme)
                help_menu.add_separator()
                
                def show_online_help():
                    webbrowser.open("https://github.com/Wetdogtaste/Film-Archiver")
                
                help_menu.add_command(label=f"{APP_NAME} Online Help", command=show_online_help)
                
            else:
                # Non-macOS menu bar (Windows/Linux)
                
                # File menu
                file_menu = tk.Menu(menubar, tearoff=0)
                menubar.add_cascade(label="File", menu=file_menu)
                file_menu.add_command(label="Exit", command=root.quit)
                
                # Help menu
                help_menu = tk.Menu(menubar, tearoff=0)
                menubar.add_cascade(label="Help", menu=help_menu)
                
                help_menu.add_command(label="Film Archiver Manual", command=open_manual)
                help_menu.add_command(label="View README", command=show_readme)
                help_menu.add_separator()
                
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
