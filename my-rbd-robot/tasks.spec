# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['tasks.py'],
    pathex=['D:\\Stage\\my-rbd-robot'],
    binaries=[],
    datas=[
        ('D:\\Stage\\my-rbd-robot\\.gitignore', '.'),
        ('D:\\Stage\\my-rbd-robot\\conda.yaml', '.'),
        ('D:\\Stage\\my-rbd-robot\\LICENSE', '.'),
        ('D:\\Stage\\my-rbd-robot\\README.md', '.'),
        ('D:\\Stage\\my-rbd-robot\\robot.yaml', '.'),
        ('D:\\Stage\\my-rbd-robot\\output', 'output'),
        ('D:\\Stage\\my-rbd-robot\\__pycache__', '__pycache__')
    ],
    hiddenimports=[],
    hookspath=[],
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
    name='tasks',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tasks',
)
