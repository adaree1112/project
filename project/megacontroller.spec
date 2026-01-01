# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# Get the absolute path to your project directory
project_dir = os.path.abspath('.')

# Create a runtime hook to set the correct path
runtime_hook_content = """
import sys
import os

# Get the path where PyInstaller extracts files
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_path = sys._MEIPASS
else:
    # Running in normal Python environment
    base_path = os.path.dirname(os.path.abspath(__file__))

# Change to the base path so relative paths work
os.chdir(base_path)
"""

# Write the runtime hook to a file
hook_file = os.path.join(project_dir, 'runtime_hook.py')
with open(hook_file, 'w') as f:
    f.write(runtime_hook_content)

a = Analysis(
    ['megacontroller.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        (os.path.join(project_dir, 'assets'), 'assets'),  # Include assets folder
    ],
    hiddenimports=[
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL._imaging',
        'LabelSpinbox',
        'LaTeXformulaimage',
        'Piecewise',
        'piecewisecubicsplines',
        'PiecewiseGraph',
        'DraggablePoint',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'mplcursors',
        'numpy',
        'scipy',
        'scipy.special',
        'scipy.ndimage',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],  # Add the runtime hook
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='megacontroller',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)