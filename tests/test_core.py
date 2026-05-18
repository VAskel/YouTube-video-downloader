import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from yt_dld.core.ffmpeg_manager import find_ffmpeg, _platform_dir


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
