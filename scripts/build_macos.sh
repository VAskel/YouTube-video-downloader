#!/bin/bash
set -e

APP_NAME="yt-dld"
BIN_DIR="$(cd "$(dirname "$0")/.." && pwd)/bin"
DIST_DIR="$(cd "$(dirname "$0")/.." && pwd)/dist"
BUILD_DIR="$(cd "$(dirname "$0")/.." && pwd)/build"

# Ensure bundled binaries directories exist
mkdir -p "$BIN_DIR/ffmpeg-macos" "$BIN_DIR/ffmpeg-windows" "$BIN_DIR/ffmpeg-linux" "$BIN_DIR/deno-macos"

# Download macOS ffmpeg if not present
if [ ! -f "$BIN_DIR/ffmpeg-macos/ffmpeg" ]; then
    echo "Downloading ffmpeg for macOS..."
    curl -SL "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip" -o /tmp/ffmpeg-macos.zip
    unzip -o /tmp/ffmpeg-macos.zip -d "$BIN_DIR/ffmpeg-macos/"
    rm /tmp/ffmpeg-macos.zip
    chmod +x "$BIN_DIR/ffmpeg-macos/ffmpeg"
fi

if [ ! -f "$BIN_DIR/ffmpeg-macos/ffprobe" ]; then
    echo "Downloading ffprobe for macOS..."
    curl -SL "https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip" -o /tmp/ffprobe-macos.zip
    unzip -o /tmp/ffprobe-macos.zip -d "$BIN_DIR/ffmpeg-macos/"
    rm /tmp/ffprobe-macos.zip
    chmod +x "$BIN_DIR/ffmpeg-macos/ffprobe"
fi

# Download Windows ffmpeg if not present
if [ ! -f "$BIN_DIR/ffmpeg-windows/ffmpeg.exe" ]; then
    echo "Downloading ffmpeg for Windows..."
    curl -SL "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" -o /tmp/ffmpeg-windows.zip
    unzip -o /tmp/ffmpeg-windows.zip -d /tmp/ffmpeg-windows-extract/
    cp /tmp/ffmpeg-windows-extract/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe "$BIN_DIR/ffmpeg-windows/"
    cp /tmp/ffmpeg-windows-extract/ffmpeg-master-latest-win64-gpl/bin/ffprobe.exe "$BIN_DIR/ffmpeg-windows/"
    rm -rf /tmp/ffmpeg-windows.zip /tmp/ffmpeg-windows-extract/
fi

# Download Linux ffmpeg if not present
if [ ! -f "$BIN_DIR/ffmpeg-linux/ffmpeg" ]; then
    echo "Downloading ffmpeg for Linux..."
    curl -fsSL --retry 5 --retry-delay 5 \
        "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz" \
        -o /tmp/ffmpeg-linux.tar.xz
    tar -xf /tmp/ffmpeg-linux.tar.xz -C /tmp/
    FFMPEG_DIR="$(find /tmp -maxdepth 1 -type d -name 'ffmpeg-*-linux64-gpl' | head -1)"
    cp "$FFMPEG_DIR/bin/ffmpeg" "$BIN_DIR/ffmpeg-linux/"
    cp "$FFMPEG_DIR/bin/ffprobe" "$BIN_DIR/ffmpeg-linux/"
    rm -rf /tmp/ffmpeg-linux.tar.xz "$FFMPEG_DIR"
fi

echo "All ffmpeg binaries ready."

# Download macOS Deno if not present
if [ ! -f "$BIN_DIR/deno-macos/deno" ]; then
    echo "Downloading Deno for macOS..."
    if [ "$(uname -m)" = "arm64" ]; then
        DENO_TARGET="aarch64-apple-darwin"
    else
        DENO_TARGET="x86_64-apple-darwin"
    fi
    curl -SL "https://github.com/denoland/deno/releases/latest/download/deno-${DENO_TARGET}.zip" -o /tmp/deno-macos.zip
    unzip -o /tmp/deno-macos.zip -d "$BIN_DIR/deno-macos/"
    rm /tmp/deno-macos.zip
    chmod +x "$BIN_DIR/deno-macos/deno"
fi

# Build macOS .app
pyinstaller \
    --name "$APP_NAME" \
    --windowed \
    --icon=src/yt_dld/resources/icons/app.icns \
    --add-data "bin/ffmpeg-macos:bin/ffmpeg-macos" \
    --add-data "bin/deno-macos:bin/deno-macos" \
    --add-data "src/yt_dld:yt_dld" \
    --hidden-import yt_dlp \
    --hidden-import PySide6 \
    --collect-all yt_dlp \
    --noconfirm \
    --clean \
    src/yt_dld/__main__.py

echo "Build complete: dist/$APP_NAME.app"
