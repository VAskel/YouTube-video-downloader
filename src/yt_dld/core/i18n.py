import locale

STRINGS = {
    "app_title": {"ru": "yt-dld — Загрузчик видео", "en": "yt-dld — Video Downloader"},
    "download_tab": {"ru": "Загрузка", "en": "Download"},
    "settings_tab": {"ru": "Настройки", "en": "Settings"},
    "url_label": {"ru": "URL:", "en": "URL:"},
    "url_placeholder": {"ru": "Вставьте ссылку на видео или плейлист...", "en": "Paste video or playlist URL..."},
    "fetch_formats": {"ru": "Получить форматы", "en": "Fetch Formats"},
    "download": {"ru": "Скачать", "en": "Download"},
    "cancel": {"ru": "Отмена", "en": "Cancel"},
    "output_path": {"ru": "Сохранить в:", "en": "Save to:"},
    "browse": {"ru": "Обзор...", "en": "Browse..."},
    "playlist_subfolder": {"ru": "Создать подпапку плейлиста", "en": "Create playlist subfolder"},
    "filter_all": {"ru": "Все", "en": "All"},
    "filter_video": {"ru": "Видео", "en": "Video"},
    "filter_audio": {"ru": "Аудио", "en": "Audio"},
    "format_id": {"ru": "ID", "en": "ID"},
    "format_resolution": {"ru": "Разрешение", "en": "Resolution"},
    "format_codec": {"ru": "Кодек", "en": "Codec"},
    "format_size": {"ru": "Размер", "en": "Size"},
    "format_note": {"ru": "Примечание", "en": "Note"},
    "best_quality": {"ru": "Лучшее качество", "en": "Best quality"},
    "status_ready": {"ru": "Готов", "en": "Ready"},
    "status_fetching": {"ru": "Получение форматов...", "en": "Fetching formats..."},
    "status_downloading": {"ru": "Скачивание...", "en": "Downloading..."},
    "status_done": {"ru": "Готово", "en": "Done"},
    "status_error": {"ru": "Ошибка", "en": "Error"},
    "speed": {"ru": "Скорость", "en": "Speed"},
    "eta": {"ru": "Осталось", "en": "ETA"},
    "playlist_progress": {"ru": "Плейлист", "en": "Playlist"},
    "settings_language": {"ru": "Язык:", "en": "Language:"},
    "settings_default_path": {"ru": "Путь сохранения по умолчанию:", "en": "Default save path:"},
    "settings_ffmpeg_path": {"ru": "Путь к ffmpeg (переопределение):", "en": "FFmpeg path (override):"},
    "menu_file": {"ru": "Файл", "en": "File"},
    "menu_exit": {"ru": "Выход", "en": "Exit"},
    "menu_help": {"ru": "Справка", "en": "Help"},
    "menu_about": {"ru": "О программе", "en": "About"},
    "about_text": {
        "ru": "yt-dld v0.1.0\nUI-оболочка над yt-dlp\n\nЗависимости: yt-dlp, PySide6, FFmpeg",
        "en": "yt-dld v0.1.0\nUI wrapper for yt-dlp\n\nDependencies: yt-dlp, PySide6, FFmpeg",
    },
    "error_no_url": {"ru": "Введите URL", "en": "Enter a URL"},
    "error_fetch": {"ru": "Ошибка получения форматов", "en": "Error fetching formats"},
    "error_download": {"ru": "Ошибка скачивания", "en": "Download error"},
    "playlist_title": {"ru": "Плейлист", "en": "Playlist"},
    "fetch_error_title": {"ru": "Ошибка", "en": "Error"},
    "format_not_found": {"ru": "Форматы не найдены", "en": "Formats not found"},
}


def _get_lang():
    try:
        loc = locale.getlocale()[0] or ""
        return "ru" if loc.startswith("ru") else "en"
    except Exception:
        return "en"


_current_lang = _get_lang()


def set_language(lang):
    global _current_lang
    if lang in ("ru", "en"):
        _current_lang = lang


def tr(key):
    entry = STRINGS.get(key, {})
    return entry.get(_current_lang, entry.get("en", key))
