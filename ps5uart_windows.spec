# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec za PS5 UART Dijagnostika – Windows
# Pokretanje: pyinstaller ps5uart_windows.spec

block_cipher = None

a = Analysis(
    ['ps5_uart_reader.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'serial',
        'serial.tools',
        'serial.tools.list_ports',
        'requests',
        'gi',
        'gi.repository.Gtk',
        'gi.repository.Gdk',
        'gi.repository.GLib',
        'gi.repository.Pango',
        'gi.repository.PangoCairo',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ps5_uart_reader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # bez crnog cmd prozora
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ps5_uart_reader',
)
