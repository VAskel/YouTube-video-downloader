#!/bin/bash
set -e

APP_NAME="yt-dld"
BIN_DIR="$(cd "$(dirname "$0")/.." && pwd)/bin"
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)/src"

mkdir -p "$BIN_DIR/ffmpeg-linux" "$BIN_DIR/deno-linux"

# Download ffmpeg for Linux if not present
if [ ! -f "$BIN_DIR/ffmpeg-linux/ffmpeg" ]; then
    echo "Downloading ffmpeg for Linux..."
    curl -SL "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz" -o /tmp/ffmpeg-linux.tar.xz
    tar -xf /tmp/ffmpeg-linux.tar.xz -C /tmp/
    cp /tmp/ffmpeg-*-amd64-static/ffmpeg "$BIN_DIR/ffmpeg-linux/"
    cp /tmp/ffmpeg-*-amd64-static/ffprobe "$BIN_DIR/ffmpeg-linux/"
    rm -rf /tmp/ffmpeg-linux.tar.xz /tmp/ffmpeg-*-amd64-static/
fi

# Download Linux Deno if not present
if [ ! -f "$BIN_DIR/deno-linux/deno" ]; then
    echo "Downloading Deno for Linux..."
    curl -SL "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip" -o /tmp/deno-linux.zip
    unzip -o /tmp/deno-linux.zip -d "$BIN_DIR/deno-linux/"
    rm /tmp/deno-linux.zip
    chmod +x "$BIN_DIR/deno-linux/deno"
fi

echo "Building $APP_NAME..."
pyinstaller \
    --name "$APP_NAME" \
    --windowed \
    --add-data "$BIN_DIR/ffmpeg-linux:bin/ffmpeg-linux" \
    --add-data "$BIN_DIR/deno-linux:bin/deno-linux" \
    --add-data "$SRC_DIR/yt_dld:yt_dld" \
    --hidden-import yt_dlp \
    --hidden-import PySide6 \
    --collect-all yt_dlp \
    --noconfirm \
    --clean \
    "$SRC_DIR/yt_dld/__main__.py"

echo "Build complete: dist/$APP_NAME"
