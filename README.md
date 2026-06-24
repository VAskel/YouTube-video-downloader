# yt-dld

A cross-platform desktop UI wrapper for [yt-dlp](https://github.com/yt-dlp/yt-dlp) with bundled FFmpeg. Built with Python and PySide6.

## Features

- **Simple download** — paste a URL, pick a format, click Download
- **Format selection** — browse available video/audio formats with resolution, codec, and size filters
- **Playlist support** — batch download playlists with per-video checkboxes, skip hidden/unavailable videos automatically
- **Per-video settings** — click ⚙ to set custom format or filename for each video in a playlist (locked once download starts)
- **Hidden video detection** — geo-blocked, private, and members-only videos are grayed out and unselectable
- **Error dialog** — after download, shows which videos failed and why, with one-click copy
- **Real-time progress** — speed, ETA, per-video playlist progress (X of Y)
- **Bundled FFmpeg** — no external dependencies; everything ships inside the app
- **Bundled Deno** — provides a JavaScript runtime for yt-dlp YouTube challenge solving
- **Cross-platform** — macOS, Windows, Linux
- **i18n** — Russian and English, auto-detected from system locale

## Screenshot

```
┌──────────────────────────────────────────────────────────────────────┐
│  yt-dld — Video Downloader                                           │
├──────────────────────────────────────────────────────────────────────┤
│  URL: [___________________________________________________]         │
│  [Fetch Formats]  [Cancel]                                           │
│                                                                       │
│  Save to: [/Users/me/Downloads                        ] [Browse...]  │
│  ☑ Create playlist subfolder                                         │
│                                                                       │
│  [Select all] [Deselect all]              Available: 8 | Unavailable: 2 │
│  ┌──┬───┬─────────────────────────────────────┬────────┬────┐       │
│  │ ☑│ 1 │ Video Title One                     │ 12:34  │ ⚙  │       │
│  │ ☑│ 2 │ Video Title Two                     │ 8:21   │ ⚙  │       │
│  │ ☐│ 3 │ Video #3 [Video hidden]             │   -    │ ⚙  │  ← grayed
│  │ ☑│ 4 │ Another Video ⚙✓                    │ 15:00  │ ⚙✓ │  ← custom
│  └──┴───┴─────────────────────────────────────┴────────┴────┘       │
│                                                                       │
│  [Download]                                                          │
│                                                                       │
│  ████████████░░░░░░░░ 67%                                            │
│  Speed: 4.2 MB/s          ETA: 0:12                                  │
│                                                                       │
│  [↓] Video Title One                                                 │
│  [✓] Another Video                                                   │
├──────────────────────────────────────────────────────────────────────┤
│  Ready  |  yt-dlp 2025.x.x                                           │
└──────────────────────────────────────────────────────────────────────┘
```

## Installation

### From source (development)

```bash
git clone https://github.com/VAskel/YouTube-video-downloader.git
cd YouTube-video-downloader
python3 -m venv .venv
source .venv/bin/activate    # macOS/Linux
# or .venv\Scripts\activate  # Windows
pip install yt-dlp PySide6
PYTHONPATH=src python -m yt_dld
```

### Pre-built binaries

Pre-built `.app` (macOS) and `.exe` (Windows) are available on the [Releases](https://github.com/VAskel/YouTube-video-downloader/releases) page.

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
| [Deno](https://deno.com/) | JavaScript runtime for YouTube challenge solving (bundled) |

## Project structure

```
YouTube-video-downloader/
├── src/yt_dld/
│   ├── __main__.py              # Entry point
│   ├── main.py                  # App bootstrap, FFmpeg init
│   ├── core/
│   │   ├── downloader.py        # yt-dlp wrapper (QThread + per-video settings)
│   │   ├── deno_manager.py      # Auto-detection of bundled/system Deno
│   │   ├── ffmpeg_manager.py    # Auto-detection of bundled FFmpeg
│   │   ├── format_fetcher.py    # Format+playlist listing, hidden video detection
│   │   └── i18n.py              # RU/EN translations
│   └── ui/
│       ├── main_window.py       # Main window, menus
│       ├── download_tab.py      # URL → formats/playlist → download flow
│       ├── format_selector.py   # Format table with video/audio/all filters
│       ├── playlist_selector.py # Playlist entries with checkboxes + per-video ⚙
│       ├── video_settings_dialog.py # Per-video format/filename settings
│       ├── error_dialog.py      # Post-download error summary with copy
│       ├── progress_widget.py   # Progress bar, speed, ETA, deduplicated log
│       └── settings_dialog.py   # App settings (language, path, ffmpeg)
├── bin/                         # Bundled FFmpeg and Deno binaries (per platform)
├── scripts/                     # PyInstaller build scripts
├── tests/                       # pytest unit tests
└── pyproject.toml
```

## License

MIT
