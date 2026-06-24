from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadQueueTask:
    url: str
    output_path: str
    selected_urls: list[str]
    per_video_settings: dict = field(default_factory=dict)
    format_id: str | None = None
    playlist_subfolder: bool = False
    playlist_title: str | None = None
    status: TaskStatus = TaskStatus.PENDING

    @property
    def title(self):
        return self.playlist_title or self.url

    @property
    def video_count(self):
        return len(self.selected_urls)


class DownloadQueue:
    def __init__(self):
        self._tasks: list[DownloadQueueTask] = []

    def __len__(self):
        return len(self._tasks)

    def __iter__(self):
        return iter(self._tasks)

    def __getitem__(self, index):
        return self._tasks[index]

    def add(self, task: DownloadQueueTask):
        self._tasks.append(task)
        return len(self._tasks) - 1

    def clear(self):
        self._tasks.clear()

    def pending(self):
        return [task for task in self._tasks if task.status == TaskStatus.PENDING]

    def next_pending(self):
        for task in self._tasks:
            if task.status == TaskStatus.PENDING:
                return task
        return None

    def cancel_pending(self):
        for task in self._tasks:
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED

    def remove_cancelled(self):
        self._tasks = [task for task in self._tasks if task.status != TaskStatus.CANCELLED]
