# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for GPA/CGPA Simulator Flask app.
Bundles ui_app.py with all templates, static files, and dependencies.
Cross-platform compatible (Windows, Linux, macOS).
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import sys
import os

block_cipher = None

# Collect all Flask and related modules
flask_datas = collect_data_files('flask')
flask_binaries = []

a = Analysis(
    ['ui_app.py'],
    pathex=[],
    binaries=flask_binaries,
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('app', 'app'),
    ] + flask_datas,
    hiddenimports=[
        'flask',
        'flask.cli',
        'flask.json',
        'flask.ctx',
        'flask.app',
        'flask.scaffold',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.security',
        'werkzeug.exceptions',
        'jinja2',
        'jinja2.ext',
        'sqlite3',
        'json',
        'markupsafe',
        'click',
        'itsdangerous',
    ] + collect_submodules('flask') + collect_submodules('werkzeug'),
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
    console=False,
    icon='gpa.ico',
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,
)
