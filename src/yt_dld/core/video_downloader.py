import glob
import os
from dataclasses import dataclass
from typing import Callable

import yt_dlp


class DownloadCancelled(Exception):
    pass


class YtLogger:
    def __init__(self, callback: Callable[[str], None]):
        self._cb = callback

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        self._cb(f"[yt-dlp] {msg}")

    def error(self, msg):
        self._cb(f"[yt-dlp] {msg}")


@dataclass(frozen=True)
class VideoDownloadSpec:
    url: str
    expected_dir: str
    display_name: str
    outtmpl: str | None = None
    format_id: str | None = None


class VideoDownloader:
    def __init__(
        self,
        base_opts: dict,
        log_callback: Callable[[str], None] | None = None,
        auth_rebuilder: Callable[[], dict] | None = None,
        cancel_checker: Callable[[], bool] | None = None,
        ydl_cls=yt_dlp.YoutubeDL,
        max_attempts: int = 3,
    ):
        self.base_opts = dict(base_opts)
        self.log_callback = log_callback or (lambda _msg: None)
        self.auth_rebuilder = auth_rebuilder
        self.cancel_checker = cancel_checker or (lambda: False)
        self.ydl_cls = ydl_cls
        self.max_attempts = max_attempts

    def download(self, spec: VideoDownloadSpec):
        for attempt in range(1, self.max_attempts + 1):
            if self.cancel_checker():
                raise DownloadCancelled("Cancelled")

            try:
                opts = self._build_opts(spec)
                with self.ydl_cls(opts) as ydl:
                    ydl.download([spec.url])

                if self._verify_output(spec.expected_dir, spec.display_name):
                    return
                err_msg = "Output file not found - leftover .part files detected"
            except DownloadCancelled:
                raise
            except Exception as e:
                err_msg = str(e)

            if attempt < self.max_attempts and not self.cancel_checker():
                self.log_callback(
                    f"[↻] {spec.display_name}: retry {attempt + 1}/{self.max_attempts} - {err_msg[:80]}"
                )
                continue
            raise Exception(err_msg)

    def _build_opts(self, spec: VideoDownloadSpec):
        opts = dict(self.base_opts)
        opts["logger"] = YtLogger(self.log_callback)

        if self.auth_rebuilder:
            opts.update(self.auth_rebuilder())

        if spec.format_id:
            opts["format"] = spec.format_id

        if spec.outtmpl:
            opts["outtmpl"] = spec.outtmpl

        return opts

    def _verify_output(self, out_dir, display_name):
        mp4_files = glob.glob(os.path.join(out_dir, "*.mp4"))
        part_files = glob.glob(os.path.join(out_dir, "*.part"))
        ytdl_files = glob.glob(os.path.join(out_dir, "*.ytdl"))
        tmp_files = part_files + ytdl_files

        newest_mp4 = None
        if mp4_files:
            newest_mp4 = max(mp4_files, key=os.path.getmtime)

        if newest_mp4 and os.path.getsize(newest_mp4) > 0:
            return True

        if tmp_files:
            names = [os.path.basename(f) for f in tmp_files[:5]]
            suffix = f" +{len(tmp_files) - 5} more" if len(tmp_files) > 5 else ""
            self.log_callback(
                f"[!] {display_name}: {len(tmp_files)} leftover file(s): {', '.join(names)}{suffix}"
            )
        return False
