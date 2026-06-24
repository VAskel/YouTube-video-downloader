import yt_dlp


class FormatFetcher:
    @staticmethod
    def fetch(url, auth_opts=None):
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": "in_playlist",
            "ignoreerrors": True,
        }
        if auth_opts:
            opts.update(auth_opts)
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if "entries" in info:
            title = info.get("title", "Playlist")
            raw_entries = info["entries"] or []
            entries = []
            available_count = 0
            unavailable_count = 0

            for idx, entry in enumerate(raw_entries):
                if entry is None:
                    entries.append({
                        "index": idx + 1,
                        "title": f"Video #{idx + 1}",
                        "url": None,
                        "available": False,
                        "duration": None,
                        "_playlist_title": title,
                    })
                    unavailable_count += 1
                elif isinstance(entry, dict):
                    entry_url = entry.get("webpage_url") or entry.get("url")
                    avail = entry.get("availability")
                    is_unavailable = (
                        avail is not None and avail != "public"
                        or entry.get("live_status") == "is_upcoming"
                        or not entry_url
                    )
                    entries.append({
                        "index": idx + 1,
                        "title": entry.get("title") or entry.get("fulltitle", f"Video #{idx + 1}"),
                        "url": entry_url,
                        "available": not is_unavailable,
                        "duration": entry.get("duration"),
                        "_playlist_title": title,
                    })
                    if is_unavailable:
                        unavailable_count += 1
                    else:
                        available_count += 1

            return {
                "type": "playlist",
                "title": title,
                "entries": entries,
                "count": len(entries),
                "available_count": available_count,
                "unavailable_count": unavailable_count,
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
