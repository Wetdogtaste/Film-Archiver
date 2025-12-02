# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Get the directory containing the spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

# Collect all PIL and tkinter submodules
hidden_imports = collect_submodules('PIL') + [
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.ttk',
    'tkcalendar',
    'babel.numbers',
    'piexif',
    'Foundation',
    'AppKit',
    'objc',
    'tkinterdnd2',
    # Application modules - these MUST be explicitly listed
    'config',
    'config.settings',
    'core',
    'core.file_manager',
    'core.preferences',
    'ui',
    'ui.main_window',
    'ui.widgets',
    'ui.widgets.toggle_switch',
    'utils',
    'utils.macos_dnd',
]

# Collect all necessary data files
datas = collect_data_files('tkcalendar') + collect_data_files('PIL')

# Add tkinterdnd2 data files (including the native tkdnd library)
try:
    tkdnd_datas = collect_data_files('tkinterdnd2')
    datas.extend(tkdnd_datas)
    print("Found tkinterdnd2 data files")
except Exception as e:
    print(f"Warning: Could not collect tkinterdnd2 data files: {e}")

# Try to find and include the tkdnd library from tkinterdnd2 package
try:
    import tkinterdnd2
    tkdnd_path = os.path.dirname(tkinterdnd2.__file__)
    tkdnd_lib = os.path.join(tkdnd_path, 'tkdnd')
    if os.path.exists(tkdnd_lib):
        # Add the entire tkdnd folder to the bundle at multiple locations
        # to ensure it can be found
        datas.append((tkdnd_lib, 'tkinterdnd2/tkdnd'))
        datas.append((tkdnd_lib, 'tkdnd'))  # Also at root level
        print(f"Found tkdnd library at: {tkdnd_lib}")
        
        # Also look for platform-specific tkdnd binaries
        for subdir in os.listdir(tkdnd_lib):
            subdir_path = os.path.join(tkdnd_lib, subdir)
            if os.path.isdir(subdir_path):
                print(f"  Including tkdnd subdirectory: {subdir}")
    else:
        print(f"tkdnd directory not found at: {tkdnd_lib}")
except ImportError:
    print("Warning: tkinterdnd2 not found, drag and drop will use native macOS fallback")

# Include application modules as data files as well (for resources)
datas.extend([
    ('config', 'config'),
    ('core', 'core'),
    ('ui', 'ui'),
    ('utils', 'utils')
])

# Include documentation files
docs_dir = os.path.dirname(spec_dir)  # Parent directory (repository root)
readme_path = os.path.join(docs_dir, 'README.md')
manual_path = os.path.join(docs_dir, 'Film Archiver Manual.pdf')

if os.path.exists(readme_path):
    datas.append((readme_path, '.'))
    print(f"Including README.md from: {readme_path}")
else:
    print(f"Warning: README.md not found at: {readme_path}")

if os.path.exists(manual_path):
    datas.append((manual_path, '.'))
    print(f"Including Film Archiver Manual.pdf from: {manual_path}")
else:
    print(f"Warning: Film Archiver Manual.pdf not found at: {manual_path}")

# Include donation icons
venmo_icon = os.path.join(spec_dir, 'venmo_icon.png')
cashapp_icon = os.path.join(spec_dir, 'cashapp_icon.png')

if os.path.exists(venmo_icon):
    datas.append((venmo_icon, '.'))
    print(f"Including venmo_icon.png from: {venmo_icon}")
else:
    print(f"Warning: venmo_icon.png not found at: {venmo_icon}")

if os.path.exists(cashapp_icon):
    datas.append((cashapp_icon, '.'))
    print(f"Including cashapp_icon.png from: {cashapp_icon}")
else:
    print(f"Warning: cashapp_icon.png not found at: {cashapp_icon}")

# Runtime hooks - runs before the main script
runtime_hooks_list = [
    os.path.join(spec_dir, 'hooks', 'rthook_tkinterdnd2.py'),
]

# Filter out runtime hooks that don't exist
runtime_hooks_list = [h for h in runtime_hooks_list if os.path.exists(h)]

a = Analysis(['main.py'],
             pathex=[spec_dir],  # Include spec directory for module resolution
             binaries=[],
             datas=datas,
             hiddenimports=hidden_imports,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=runtime_hooks_list,
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Film Archiver',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None)

coll = COLLECT(exe,
              a.binaries,
              a.zipfiles,
              a.datas,
              strip=False,
              upx=True,
              upx_exclude=[],
              name='Film Archiver')

app = BUNDLE(coll,
            name='Film Archiver.app',
            icon='AppIcon.icns',
            bundle_identifier='com.filmarchiver.app',
            info_plist={
                'LSMinimumSystemVersion': '10.13.0',
                'NSHighResolutionCapable': True,
                'CFBundleShortVersionString': '1.2.2',
                'CFBundleVersion': '1.2.2',
                'NSHumanReadableCopyright': '© 2024-2025 Michael Ziebell',
                'NSAppleEventsUsageDescription': 'Please allow access to execute applescript for folder operations.'
            })
