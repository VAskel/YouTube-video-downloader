import yt_dlp


class FormatFetcher:
    @staticmethod
    def fetch(url):
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if "entries" in info:
            title = info.get("title", "Playlist")
            entries = info["entries"] or []
            is_playlist = True
            formats = []
            for entry in entries:
                if entry:
                    entry["_playlist_title"] = title
                formats.append(entry)
            return {
                "type": "playlist",
                "title": title,
                "entries": entries,
                "count": len(entries),
            }

        formats = info.get("formats", [])
        video_formats = []
        audio_formats = []

        for f in formats:
            fmt = {
                "id": f.get("format_id", ""),
                "ext": f.get("ext", ""),
                "resolution": f.get("resolution") or f"{f.get('width', '?')}x{f.get('height', '?')}",
                "fps": f.get("fps"),
                "codec": f.get("vcodec", "none"),
                "acodec": f.get("acodec", "none"),
                "filesize": f.get("filesize"),
                "filesize_approx": f.get("filesize_approx"),
                "tbr": f.get("tbr"),
                "format_note": f.get("format_note", ""),
                "has_video": f.get("vcodec", "none") != "none",
                "has_audio": f.get("acodec", "none") != "none",
            }

            if fmt["has_video"]:
                video_formats.append(fmt)
            if fmt["has_audio"] and not fmt["has_video"]:
                audio_formats.append(fmt)

            if fmt["has_video"] and fmt["has_audio"]:
                video_formats.append(fmt)

        return {
            "type": "video",
            "title": info.get("title", "Unknown"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "uploader": info.get("uploader"),
            "video_formats": video_formats,
            "audio_formats": audio_formats,
        }
