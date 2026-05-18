import os

from PySide6.QtCore import QThread, Signal
import yt_dlp


class DownloadWorker(QThread):
    progress = Signal(dict)
    finished = Signal(str, str)
    error = Signal(str)

    def __init__(self, url, output_path, format_id=None, playlist_subfolder=False, ffmpeg_path=None, parent=None):
        super().__init__(parent)
        self.url = url
        self.output_path = output_path
        self.format_id = format_id
        self.playlist_subfolder = playlist_subfolder
        self.ffmpeg_path = ffmpeg_path
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def _progress_hook(self, d):
        if self._cancelled:
            raise Exception("Cancelled")

        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            speed = d.get("speed") or 0
            eta = d.get("eta") or 0

            pct = (downloaded / total * 100) if total > 0 else 0

            playlist_idx = d.get("info_dict", {}).get("playlist_index")
            playlist_count = d.get("info_dict", {}).get("playlist_count") or d.get("info_dict", {}).get("n_entries")

            self.progress.emit({
                "status": "downloading",
                "percent": pct,
                "total_bytes": total,
                "downloaded_bytes": downloaded,
                "speed": speed,
                "eta": eta,
                "filename": d.get("filename", ""),
                "playlist_index": playlist_idx,
                "playlist_count": playlist_count,
            })
        elif d["status"] == "finished":
            self.progress.emit({
                "status": "finished",
                "percent": 100,
                "filename": d.get("filename", ""),
            })

    def run(self):
        out_tmpl = os.path.join(self.output_path, "%(title)s.%(ext)s")
        if self.playlist_subfolder:
            out_tmpl = os.path.join(self.output_path, "%(playlist_title)s", "%(playlist_index)s - %(title)s.%(ext)s")

        opts = {
            "outtmpl": out_tmpl,
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
            "noplaylist": False,
            "merge_output_format": "mp4",
        }

        if self.format_id and self.format_id != "best":
            opts["format"] = self.format_id
        else:
            opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

        if self.ffmpeg_path:
            ffmpeg_dir = os.path.dirname(self.ffmpeg_path)
            opts["ffmpeg_location"] = ffmpeg_dir

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url])
            if not self._cancelled:
                self.finished.emit(self.url, self.output_path)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(str(e))
