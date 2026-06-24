@echo off
set APP_NAME=yt-dld
set BIN_DIR=%~dp0..\bin
set SRC_DIR=%~dp0..\src

if not exist "%BIN_DIR%\ffmpeg-windows" mkdir "%BIN_DIR%\ffmpeg-windows"
if not exist "%BIN_DIR%\deno-windows" mkdir "%BIN_DIR%\deno-windows"

REM Download ffmpeg for Windows if not present
if not exist "%BIN_DIR%\ffmpeg-windows\ffmpeg.exe" (
    echo Downloading ffmpeg for Windows...
    curl -SL "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" -o "%TEMP%\ffmpeg-windows.zip"
    powershell -Command "Expand-Archive '%TEMP%\ffmpeg-windows.zip' '%TEMP%\ffmpeg-windows-extract'"
    for /d %%d in ("%TEMP%\ffmpeg-windows-extract\ffmpeg-master-latest-win64-gpl\bin") do (
        copy "%%d\ffmpeg.exe" "%BIN_DIR%\ffmpeg-windows\"
        copy "%%d\ffprobe.exe" "%BIN_DIR%\ffmpeg-windows\"
    )
)

REM Download Deno for Windows if not present
if not exist "%BIN_DIR%\deno-windows\deno.exe" (
    echo Downloading Deno for Windows...
    curl -SL "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip" -o "%TEMP%\deno-windows.zip"
    powershell -Command "Expand-Archive -Force '%TEMP%\deno-windows.zip' '%TEMP%\deno-windows-extract'"
    copy "%TEMP%\deno-windows-extract\deno.exe" "%BIN_DIR%\deno-windows\"
)

echo Building %APP_NAME%.exe...
pyinstaller ^
    --name "%APP_NAME%" ^
    --windowed ^
    --add-data "%BIN_DIR%\ffmpeg-windows;bin\ffmpeg-windows" ^
    --add-data "%BIN_DIR%\deno-windows;bin\deno-windows" ^
    --add-data "%SRC_DIR%\yt_dld;yt_dld" ^
    --hidden-import yt_dlp ^
    --hidden-import PySide6 ^
    --collect-all yt_dlp ^
    --noconfirm ^
    --clean ^
    "%SRC_DIR%\yt_dld\__main__.py"

echo Build complete: dist\%APP_NAME%.exe
pause
