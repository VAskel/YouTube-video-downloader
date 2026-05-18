# yt-dld

A cross-platform desktop UI wrapper for [yt-dlp](https://github.com/yt-dlp/yt-dlp) with bundled FFmpeg. Built with Python and PySide6.

## Features

- **Simple download** — paste a URL, pick a format, click Download
- **Format selection** — browse available video/audio formats with resolution, codec, and size filters
- **Playlist support** — batch download entire playlists with per-video progress and optional subfolder creation
- **Real-time progress** — speed, ETA, and per-video playlist progress (X of Y)
- **Bundled FFmpeg** — no external dependencies; everything ships inside the app
- **Cross-platform** — macOS, Windows, Linux
- **i18n** — Russian and English, auto-detected from system locale

## Screenshot

```
┌─────────────────────────────────────────────────────────┐
│  yt-dld — Video Downloader                              │
├─────────────────────────────────────────────────────────┤
│  URL: [________________________________________]        │
│  [Fetch Formats]  [Download]  [Cancel]                  │
│                                                          │
│  Save to: [/Users/me/Downloads          ] [Browse...]   │
│  ☑ Create playlist subfolder                            │
│                                                          │
│  ┌─ All  ○ Video  ○ Audio  ☑ Best quality ─────────┐   │
│  │ ID      │ Resolution │ Codec        │ Size       │   │
│  ├─────────┼────────────┼──────────────┼────────────┤   │
│  │ 137     │ 1080p      │ avc1/none    │ ~120 MB    │   │
│  │ 136     │ 720p       │ avc1/none    │ ~80 MB     │   │
│  │ 140     │ audio only │ none/mp4a    │ ~5 MB      │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ████████████░░░░░░░░ 67%                                │
│  Speed: 4.2 MB/s          ETA: 0:12                      │
│                                                          │
│  [↓] Video Title.mp4                                     │
│  [✓] Another Video.mp4                                   │
├─────────────────────────────────────────────────────────┤
│  Ready  |  yt-dlp 2025.x.x                               │
└─────────────────────────────────────────────────────────┘
```

## Installation

### From source (development)

```bash
git clone https://github.com/yourname/yt-dld.git
cd yt-dld
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
python -m yt_dld
```

### Pre-built binaries

Pre-built `.app` (macOS) and `.exe` (Windows) are available on the [Releases](https://github.com/yourname/yt-dld/releases) page.

## Build

### macOS

```bash
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh
# Output: dist/yt-dld.app
```

### Windows

```cmd
scripts\build_windows.bat
REM Output: dist\yt-dld.exe
```

### Linux

```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
# Output: dist/yt-dld
```

Build scripts automatically download FFmpeg binaries for all platforms before bundling.

## Settings

Settings are stored in `~/.yt_dld/settings.json`:

- **Language** — Russian / English
- **Default save path** — where downloads go by default
- **FFmpeg path** — override auto-detected FFmpeg binary

## Dependencies

| Package | Purpose |
|---------|---------|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube/video extraction and downloading |
| [PySide6](https://pypi.org/project/PySide6/) | Qt for Python GUI framework (LGPL) |
| [FFmpeg](https://ffmpeg.org/) | Audio/video processing (bundled as static binaries) |

## Project structure

```
yt_dld/
├── src/yt_dld/
│   ├── __main__.py           # Entry point
│   ├── main.py               # App bootstrap, FFmpeg init
│   ├── core/
│   │   ├── downloader.py     # yt-dlp wrapper (QThread + progress signals)
│   │   ├── ffmpeg_manager.py # Auto-detection of bundled FFmpeg
│   │   ├── format_fetcher.py # Format listing via yt-dlp API
│   │   └── i18n.py           # RU/EN translations
│   └── ui/
│       ├── main_window.py    # Main window, menus, tabs
│       ├── download_tab.py   # URL input → formats → download flow
│       ├── format_selector.py # Format table with filters
│       ├── progress_widget.py # Progress bar, speed, ETA, log
│       └── settings_dialog.py # App settings dialog
├── bin/                      # Bundled FFmpeg binaries (per platform)
├── scripts/                  # PyInstaller build scripts
├── tests/                    # pytest unit tests
└── pyproject.toml
```

## License

MIT
