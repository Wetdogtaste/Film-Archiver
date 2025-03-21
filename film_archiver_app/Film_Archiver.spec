# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

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
    'objc'
]

# Collect all necessary data files
datas = collect_data_files('tkcalendar') + collect_data_files('PIL')
datas.extend([
    ('config', 'config'),
    ('core', 'core'),
    ('ui', 'ui'),
    ('utils', 'utils')
])

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=datas,
             hiddenimports=hidden_imports,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
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
          console=True,
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
            icon='AppIcon.icns',  # This line implements the icon
            bundle_identifier='com.filmarchiver.app',
            info_plist={
                'LSMinimumSystemVersion': '10.13.0',
                'NSHighResolutionCapable': True,
                'CFBundleShortVersionString': '1.0.0',
                'CFBundleVersion': '1.0.0',
                'NSAppleEventsUsageDescription': 'Please allow access to execute applescript for folder operations.'
            })
