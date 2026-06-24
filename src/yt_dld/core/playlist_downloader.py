from dataclasses import dataclass
from typing import Callable, Sequence

from yt_dld.core.video_downloader import DownloadCancelled, VideoDownloader, VideoDownloadSpec


@dataclass(frozen=True)
class PlaylistItemError:
    url: str
    title: str
    error: str


class PlaylistDownloader:
    def __init__(
        self,
        video_downloader: VideoDownloader,
        item_start_callback: Callable[[VideoDownloadSpec, int, int], None] | None = None,
        item_error_callback: Callable[[PlaylistItemError], None] | None = None,
        cancel_checker: Callable[[], bool] | None = None,
    ):
        self.video_downloader = video_downloader
        self.item_start_callback = item_start_callback or (lambda _spec, _idx, _total: None)
        self.item_error_callback = item_error_callback or (lambda _err: None)
        self.cancel_checker = cancel_checker or (lambda: False)

    def download(self, videos: Sequence[VideoDownloadSpec]) -> list[PlaylistItemError]:
        errors = []
        total = len(videos)

        for idx, spec in enumerate(videos, start=1):
            if self.cancel_checker():
                break

            self.item_start_callback(spec, idx, total)

            try:
                self.video_downloader.download(spec)
            except DownloadCancelled:
                break
            except Exception as e:
                err = PlaylistItemError(
                    url=spec.url,
                    title=spec.display_name,
                    error=str(e),
                )
                errors.append(err)
                self.item_error_callback(err)

        return errors
