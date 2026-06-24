import unittest
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from yt_dld.core.ffmpeg_manager import find_ffmpeg, _platform_dir
from yt_dld.core.download_queue import DownloadQueue, DownloadQueueTask, TaskStatus
from yt_dld.core.playlist_downloader import PlaylistDownloader
from yt_dld.core.video_downloader import DownloadCancelled, VideoDownloader, VideoDownloadSpec


class TestFfmpegManager(unittest.TestCase):
    def test_platform_dir(self):
        d = _platform_dir()
        self.assertIn(d, ("ffmpeg-macos", "ffmpeg-windows", "ffmpeg-linux"))

    def test_find_ffmpeg(self):
        ffmpeg, ffprobe = find_ffmpeg()
        self.assertTrue(os.path.isfile(ffmpeg))
        self.assertTrue(os.path.isfile(ffprobe))


class TestFormatFetcher(unittest.TestCase):
    def test_fetch_formats_structure(self):
        from yt_dld.core.format_fetcher import FormatFetcher

        info = FormatFetcher.fetch("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertIn(info["type"], ("video", "playlist"))

        if info["type"] == "video":
            self.assertIn("video_formats", info)
            self.assertIn("audio_formats", info)
            self.assertIn("title", info)
            self.assertIsInstance(info["video_formats"], list)
            for fmt in info["video_formats"]:
                self.assertIn("id", fmt)
                self.assertIn("resolution", fmt)


class TestVideoDownloader(unittest.TestCase):
    def test_download_applies_item_overrides(self):
        calls = []

        with tempfile.TemporaryDirectory() as tmp:
            class FakeYDL:
                def __init__(self, opts):
                    self.opts = opts

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

                def download(self, urls):
                    calls.append((self.opts, urls))
                    Path(tmp, "video.mp4").write_bytes(b"ok")

            downloader = VideoDownloader(
                {"format": "best"},
                ydl_cls=FakeYDL,
            )

            downloader.download(
                VideoDownloadSpec(
                    url="https://example.test/video",
                    expected_dir=tmp,
                    display_name="Video",
                    outtmpl=os.path.join(tmp, "custom.%(ext)s"),
                    format_id="18",
                )
            )

        opts, urls = calls[0]
        self.assertEqual(urls, ["https://example.test/video"])
        self.assertEqual(opts["format"], "18")
        self.assertTrue(opts["outtmpl"].endswith("custom.%(ext)s"))
        self.assertIn("logger", opts)

    def test_download_retries_when_output_is_missing(self):
        calls = []
        logs = []

        with tempfile.TemporaryDirectory() as tmp:
            class FakeYDL:
                def __init__(self, opts):
                    self.opts = opts

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

                def download(self, urls):
                    calls.append(urls)
                    if len(calls) == 2:
                        Path(tmp, "video.mp4").write_bytes(b"ok")

            downloader = VideoDownloader(
                {},
                log_callback=logs.append,
                ydl_cls=FakeYDL,
            )

            downloader.download(
                VideoDownloadSpec(
                    url="https://example.test/video",
                    expected_dir=tmp,
                    display_name="Video",
                )
            )

        self.assertEqual(len(calls), 2)
        self.assertTrue(any("retry 2/3" in log for log in logs))

    def test_download_respects_cancel_before_start(self):
        calls = []

        class FakeYDL:
            def __init__(self, opts):
                calls.append(opts)

        downloader = VideoDownloader(
            {},
            cancel_checker=lambda: True,
            ydl_cls=FakeYDL,
        )

        with self.assertRaises(DownloadCancelled):
            downloader.download(
                VideoDownloadSpec(
                    url="https://example.test/video",
                    expected_dir="/tmp",
                    display_name="Video",
                )
            )

        self.assertEqual(calls, [])


class TestPlaylistDownloader(unittest.TestCase):
    def test_download_continues_after_item_error(self):
        started = []
        errors = []

        class FakeVideoDownloader:
            def download(self, spec):
                if spec.url == "bad":
                    raise Exception("boom")

        downloader = PlaylistDownloader(
            FakeVideoDownloader(),
            item_start_callback=lambda spec, idx, total: started.append((spec.url, idx, total)),
            item_error_callback=errors.append,
        )

        result = downloader.download([
            VideoDownloadSpec(url="bad", expected_dir="/tmp", display_name="Bad"),
            VideoDownloadSpec(url="good", expected_dir="/tmp", display_name="Good"),
        ])

        self.assertEqual(started, [("bad", 1, 2), ("good", 2, 2)])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].url, "bad")
        self.assertEqual(errors, result)

    def test_download_stops_when_cancelled(self):
        calls = []
        cancelled = {"value": False}

        class FakeVideoDownloader:
            def download(self, spec):
                calls.append(spec.url)
                cancelled["value"] = True

        downloader = PlaylistDownloader(
            FakeVideoDownloader(),
            cancel_checker=lambda: cancelled["value"],
        )

        result = downloader.download([
            VideoDownloadSpec(url="one", expected_dir="/tmp", display_name="One"),
            VideoDownloadSpec(url="two", expected_dir="/tmp", display_name="Two"),
        ])

        self.assertEqual(calls, ["one"])
        self.assertEqual(result, [])

    def test_download_stops_on_download_cancelled(self):
        calls = []

        class FakeVideoDownloader:
            def download(self, spec):
                calls.append(spec.url)
                raise DownloadCancelled("Cancelled")

        downloader = PlaylistDownloader(FakeVideoDownloader())

        result = downloader.download([
            VideoDownloadSpec(url="one", expected_dir="/tmp", display_name="One"),
            VideoDownloadSpec(url="two", expected_dir="/tmp", display_name="Two"),
        ])

        self.assertEqual(calls, ["one"])
        self.assertEqual(result, [])


class TestDownloadQueue(unittest.TestCase):
    def test_add_and_next_pending_preserve_order(self):
        queue = DownloadQueue()
        first = DownloadQueueTask(
            url="playlist",
            output_path="/tmp",
            selected_urls=["one", "two"],
            playlist_title="Playlist",
        )
        second = DownloadQueueTask(
            url="video",
            output_path="/tmp",
            selected_urls=["video"],
        )

        self.assertEqual(queue.add(first), 0)
        self.assertEqual(queue.add(second), 1)

        self.assertEqual(len(queue), 2)
        self.assertEqual(queue.next_pending(), first)
        self.assertEqual(first.title, "Playlist")
        self.assertEqual(first.video_count, 2)

    def test_next_pending_skips_non_pending_tasks(self):
        queue = DownloadQueue()
        done = DownloadQueueTask(url="done", output_path="/tmp", selected_urls=["done"])
        pending = DownloadQueueTask(url="pending", output_path="/tmp", selected_urls=["pending"])
        done.status = TaskStatus.DONE

        queue.add(done)
        queue.add(pending)

        self.assertEqual(queue.pending(), [pending])
        self.assertEqual(queue.next_pending(), pending)

    def test_cancel_pending_and_remove_cancelled(self):
        queue = DownloadQueue()
        active = DownloadQueueTask(url="active", output_path="/tmp", selected_urls=["active"])
        pending = DownloadQueueTask(url="pending", output_path="/tmp", selected_urls=["pending"])
        active.status = TaskStatus.ACTIVE

        queue.add(active)
        queue.add(pending)
        queue.cancel_pending()

        self.assertEqual(active.status, TaskStatus.ACTIVE)
        self.assertEqual(pending.status, TaskStatus.CANCELLED)

        queue.remove_cancelled()

        self.assertEqual(list(queue), [active])


class TestI18n(unittest.TestCase):
    def test_tr_en(self):
        from yt_dld.core.i18n import tr, set_language
        set_language("en")
        self.assertEqual(tr("download_tab"), "Download")

    def test_tr_ru(self):
        from yt_dld.core.i18n import tr, set_language
        set_language("ru")
        self.assertEqual(tr("download_tab"), "Загрузка")

    def test_unknown_key_fallback(self):
        from yt_dld.core.i18n import tr
        self.assertEqual(tr("nonexistent_key"), "nonexistent_key")
