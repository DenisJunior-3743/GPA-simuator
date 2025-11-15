# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for GPA/CGPA Simulator Flask app.
Bundles ui_app.py with all templates, static files, and dependencies.
"""

from PyInstaller.utils.hooks import collect_data_files
import sys
import os

block_cipher = None

a = Analysis(
    ['ui_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('app', 'app'),
    ],
    hiddenimports=[
        'flask',
        'werkzeug',
        'sqlite3',
        'jinja2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='gpa_simulator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
