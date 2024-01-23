#!/bin/bash
pyinstaller --clean --onefile main.py
mv dist/main ~/.local/bin/flameshot-uploader
mv flameshot-uploader.desktop ~/.local/share/applications/