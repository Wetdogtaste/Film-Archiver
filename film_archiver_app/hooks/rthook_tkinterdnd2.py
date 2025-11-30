"""
Runtime hook for tkinterdnd2 - sets up the tkdnd library path for bundled apps.

This hook runs at application startup before the main script executes.
It ensures that tkinterdnd2 can find its tkdnd Tcl extension in the bundled app.
"""
import os
import sys
import platform

def _get_bundle_dir():
    """Get the directory where the bundled app resources are located."""
    if getattr(sys, 'frozen', False):
        # Running as a bundled app
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller's temp directory
            return sys._MEIPASS
        else:
            # Running from the app directory
            return os.path.dirname(sys.executable)
    else:
        # Running in development
        return os.path.dirname(os.path.abspath(__file__))

def _get_tkdnd_platform():
    """Get the platform-specific tkdnd subdirectory name."""
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

def _setup_tkdnd_path():
    """Set up the tkdnd library path for the bundled app."""
    if not getattr(sys, 'frozen', False):
        return
    
    bundle_dir = _get_bundle_dir()
    platform_dir = _get_tkdnd_platform()
    
    # Possible locations for tkdnd in the bundle (with platform-specific subdirectory)
    tkdnd_locations = [
        os.path.join(bundle_dir, 'tkinterdnd2', 'tkdnd', platform_dir),
        os.path.join(bundle_dir, 'tkdnd', platform_dir),
        os.path.join(bundle_dir, 'tkinterdnd2', 'tkdnd'),
        os.path.join(bundle_dir, 'tkdnd'),
        os.path.join(bundle_dir, 'lib', 'tkdnd', platform_dir),
        os.path.join(bundle_dir, 'lib', 'tkdnd'),
    ]
    
    for tkdnd_path in tkdnd_locations:
        if os.path.exists(tkdnd_path):
            # Set environment variable for tkinterdnd2 to find tkdnd
            os.environ['TKDND_LIBRARY'] = tkdnd_path
            os.environ['TK_DND_PATH'] = tkdnd_path
            break

# Run setup when this hook is loaded
_setup_tkdnd_path()
