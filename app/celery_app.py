from __future__ import annotations

import os
from celery import Celery
from app.utils.env import load_env_file


load_env_file()
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
backend_url = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

celery_app = Celery(
    "financial_ai",
    broker=broker_url,
    backend=backend_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Ensure tasks are registered
celery_app.autodiscover_tasks(["app.tasks"])
