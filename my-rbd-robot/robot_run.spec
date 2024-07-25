# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('robot')

a = Analysis(['robot_run.py'],
             pathex=['D:/Stage/my-rbd-robot'],
             binaries=[('D:/Stage/my-rbd-robot/dependance/robot-framework/bin/robot.exe', 'robot-framework')],
             datas=[('./dependance/robot-framework', 'robot-framework')],
             hiddenimports=hiddenimports,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             cipher=None,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=None)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='robot_run',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True)
