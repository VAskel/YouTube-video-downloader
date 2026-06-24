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
    "select_all": {"ru": "Выбрать все", "en": "Select all"},
    "deselect_all": {"ru": "Снять все", "en": "Deselect all"},
    "available_count": {"ru": "Доступно", "en": "Available"},
    "unavailable_count": {"ru": "Недоступно", "en": "Unavailable"},
    "hidden_video": {"ru": "Видео скрыто", "en": "Video hidden"},
    "playlist_skip_unavailable": {"ru": "Пропущено %d недоступных видео", "en": "Skipped %d unavailable videos"},
    "error_dialog_title": {"ru": "Ошибки скачивания", "en": "Download errors"},
    "errors_count": {"ru": "%d из %d видео не скачались", "en": "%d of %d videos failed"},
    "error_table_index": {"ru": "№", "en": "#"},
    "error_table_title": {"ru": "Название", "en": "Title"},
    "error_table_error": {"ru": "Ошибка", "en": "Error"},
    "copy_errors": {"ru": "Копировать", "en": "Copy"},
    "close": {"ru": "Закрыть", "en": "Close"},
    "no_videos_selected": {"ru": "Не выбрано ни одного видео", "en": "No videos selected"},
    "item_skipped": {"ru": "Пропущено", "en": "Skipped"},
    "item_error": {"ru": "Ошибка", "en": "Error"},
    "fetch_first": {"ru": "Сначала нажмите Fetch", "en": "Click Fetch first"},
    "duration": {"ru": "Длит.", "en": "Duration"},
    "per_video_settings": {"ru": "Настройки скачивания", "en": "Download settings"},
    "settings_format": {"ru": "Формат:", "en": "Format:"},
    "settings_format_best": {"ru": "Лучшее качество", "en": "Best quality"},
    "settings_format_video_only": {"ru": "Только видео (mp4)", "en": "Video only (mp4)"},
    "settings_format_audio_only": {"ru": "Только аудио (m4a)", "en": "Audio only (m4a)"},
    "settings_format_video_audio": {"ru": "Видео + аудио (mp4)", "en": "Video + Audio (mp4)"},
    "settings_filename": {"ru": "Имя файла:", "en": "Filename:"},
    "settings_apply": {"ru": "Применить", "en": "Apply"},
    "auth_title": {"ru": "Авторизация YouTube", "en": "YouTube Auth"},
    "auth_none": {"ru": "Без авторизации", "en": "No auth"},
    "auth_browser": {"ru": "Cookies из браузера", "en": "Cookies from browser"},
    "auth_file": {"ru": "Файл cookies.txt", "en": "Cookies file"},
    "auth_login": {"ru": "Логин / пароль", "en": "Username / password"},
    "auth_browser_select": {"ru": "Браузер:", "en": "Browser:"},
    "auth_cookies_file": {"ru": "Файл cookies:", "en": "Cookies file:"},
    "auth_username": {"ru": "Логин:", "en": "Username:"},
    "auth_password": {"ru": "Пароль:", "en": "Password:"},
    "auth_browser_hint": {
        "ru": "При первом использовании macOS запросит доступ к Keychain. Нажмите «Разрешить».",
        "en": "On first use, macOS will ask for Keychain access. Click «Allow»."
    },
    "auth_browser_safari_removed": {
        "ru": "Safari не поддерживается (блокировка sandbox на macOS). Используйте Chrome или Firefox.",
        "en": "Safari is not supported (sandbox restriction on macOS). Use Chrome or Firefox."
    },
    "queue_title": {
        "ru": "Очередь загрузок",
        "en": "Download queue",
    },
    "queue_empty": {
        "ru": "Очередь пуста",
        "en": "Queue is empty",
    },
    "queue_pending": {
        "ru": "В очереди: %d",
        "en": "In queue: %d",
    },
    "queue_downloading": {
        "ru": "Скачивается: %s",
        "en": "Downloading: %s",
    },
    "queue_added": {
        "ru": "Добавлено в очередь: %s (%d видео)",
        "en": "Added to queue: %s (%d videos)",
    },
    "queue_clear": {
        "ru": "Очистить очередь",
        "en": "Clear queue",
    },
    "queue_remove": {
        "ru": "Удалить",
        "en": "Remove",
    },
    "queue_confirm_clear": {
        "ru": "Очистить всю очередь (%d плейлистов)?",
        "en": "Clear entire queue (%d playlists)?",
    },
    "queue_completed": {
        "ru": "✓ %s завершён",
        "en": "✓ %s completed",
    },
    "add_to_queue": {
        "ru": "В очередь",
        "en": "Add to queue",
    },
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
