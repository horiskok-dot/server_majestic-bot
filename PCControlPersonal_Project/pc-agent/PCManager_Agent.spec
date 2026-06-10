# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['agent.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.ico', '.'), ('logo.png', '.')],
    hiddenimports=['psutil', 'requests', 'requests.adapters', 'urllib3', 'certifi', 'websockets', 'websockets.sync', 'websockets.sync.client', 'pystray'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    name='PCManager_Agent',
    icon=r'c:\Users\horis\Downloads\PCManagerBot_Setup_v2\PCControlPersonal_Project\pc-agent\icon.ico',
    version=r'c:\Users\horis\Downloads\PCManagerBot_Setup_v2\PCControlPersonal_Project\pc-agent\file_version_info.txt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
