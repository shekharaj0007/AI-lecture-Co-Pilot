import logging
import threading

from celery import Celery

from app.core.config import settings

logger = logging.getLogger(__name__)

if settings.celery_eager:
    celery_app = Celery("lecture_copilot", broker="memory://", backend="cache+memory://")
else:
    celery_app = Celery(
        "lecture_copilot",
        broker=settings.redis_url,
        backend=settings.redis_url,
    )

celery_app.conf.update(
    include=["app.workers.pipeline"],
    task_track_started=True,
    task_time_limit=60 * 60 * 4,
)


def _ensure_tasks_loaded() -> None:
    import app.workers.pipeline  # noqa: F401


def enqueue_task(task_name: str, args: list) -> None:
    _ensure_tasks_loaded()
    task = celery_app.tasks.get(task_name)
    if task is None:
        raise ValueError(f"Unknown task: {task_name}")

    def run() -> None:
        try:
            task.run(*args)
        except Exception:
            logger.exception("Task failed: %s %s", task_name, args)

    if settings.celery_eager:
        threading.Thread(target=run, daemon=True).start()
    else:
        task.apply_async(args=args)


_ensure_tasks_loaded()
