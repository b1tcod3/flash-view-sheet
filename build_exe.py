import os
import sys
from PyInstaller.__main__ import run

if sys.platform != "win32":
    print("ADVERTENCIA: Este script está diseñado para Windows.")
    print("En Linux/Mac los separadores de --add-data deben ser ':' no ';'")

def build_executable():
    """Build ejecutable para Windows"""

    if os.path.exists("build"):
        import shutil
        shutil.rmtree("build")
    if os.path.exists("dist"):
        import shutil
        shutil.rmtree("dist")

    args = [
        'main.py',
        '--onefile',
        '--windowed',
        '--name=FlashSheet',
        '--icon=assets/logo.png',
        '--add-data=assets;assets',
        '--add-data=core;core',
        '--add-data=app;app',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=psutil',
        '--hidden-import=numpy',
        '--collect-all=numpy',
        '--distpath=dist/windows',
        '--workpath=build/windows',
    ]

    run(args)

if __name__ == "__main__":
    build_executable()
