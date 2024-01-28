#!/bin/bash
pyinstaller --clean --onefile main.py
mv dist/flameshot-uploader ~/.local/bin/flameshot-uploader
cp flameshot-uploader.desktop ~/.local/share/applications/