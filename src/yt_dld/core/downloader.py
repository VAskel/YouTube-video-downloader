import os

from PySide6.QtCore import QThread, Signal
import yt_dlp


class DownloadWorker(QThread):
    progress = Signal(dict)
    item_error = Signal(dict)
    finished = Signal(str, str, object)
    error = Signal(str)

    def __init__(self, url, output_path, format_id=None, playlist_subfolder=False,
                 ffmpeg_path=None, selected_urls=None, parent=None):
        super().__init__(parent)
        self.url = url
        self.output_path = output_path
        self.format_id = format_id
        self.playlist_subfolder = playlist_subfolder
        self.ffmpeg_path = ffmpeg_path
        self.selected_urls = selected_urls or []
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

            info_dict = d.get("info_dict", {})
            playlist_idx = info_dict.get("playlist_index")
            playlist_count = info_dict.get("playlist_count") or info_dict.get("n_entries")

            filename = d.get("filename", "")
            if filename:
                filename = os.path.splitext(os.path.basename(filename))[0]
            elif info_dict.get("title"):
                filename = info_dict["title"]

            self.progress.emit({
                "status": "downloading",
                "percent": pct,
                "total_bytes": total,
                "downloaded_bytes": downloaded,
                "speed": speed,
                "eta": eta,
                "filename": filename,
                "playlist_index": playlist_idx,
                "playlist_count": playlist_count,
            })
        elif d["status"] == "finished":
            info_dict = d.get("info_dict", {})
            filename = d.get("filename", "")
            if filename:
                filename = os.path.splitext(os.path.basename(filename))[0]
            self.progress.emit({
                "status": "finished",
                "percent": 100,
                "filename": filename,
            })

    def _build_opts(self, extra=None):
        out_tmpl = os.path.join(self.output_path, "%(title)s.%(ext)s")
        if self.playlist_subfolder:
            out_tmpl = os.path.join(self.output_path, "%(playlist_title)s", "%(playlist_index)s - %(title)s.%(ext)s")

        opts = {
            "outtmpl": out_tmpl,
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": "mp4",
            "ignoreerrors": True,
            "progress_hooks": [self._progress_hook],
        }

        if self.format_id and self.format_id != "best":
            opts["format"] = self.format_id
        else:
            opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

        if self.ffmpeg_path:
            opts["ffmpeg_location"] = os.path.dirname(self.ffmpeg_path)

        if extra:
            opts.update(extra)

        return opts

    def run(self):
        errors = []
        try:
            if self.selected_urls:
                errors = self._download_selected()
            else:
                errors = self._download_playlist()

            if not self._cancelled:
                self.finished.emit(self.url, self.output_path, errors if errors else None)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(str(e))

    def _download_selected(self):
        opts = self._build_opts({"noplaylist": True})
        errors = []

        for i, u in enumerate(self.selected_urls):
            if self._cancelled:
                break
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([u])
            except Exception as e:
                err = {"url": u, "title": u, "error": str(e)}
                errors.append(err)
                self.item_error.emit(err)

        return errors

    def _download_playlist(self):
        opts = self._build_opts({"noplaylist": False})
        errors = []

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url])
        except Exception as e:
            err = {"url": self.url, "title": self.url, "error": str(e)}
            errors.append(err)
            self.item_error.emit(err)

        return errors
