from __future__ import absolute_import, unicode_literals

import os

import dotenv  # type: ignore
from celery import Celery

dotenv.read_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"), override=True
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "product_scraper.settings")

app: Celery = Celery("product_scraper")  # type: ignore

app.config_from_object("django.conf:settings", namespace="CELERY")  # type: ignore[attr-defined]

app.autodiscover_tasks()  # type: ignore

app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"  # type: ignore
