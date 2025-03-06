from __future__ import absolute_import, unicode_literals
import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab

import dotenv

dotenv.read_dotenv(os.path.join(os.path.dirname(
    os.path.dirname(__file__)), '.env'), override=True)
    
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_scraper.settings')

app = Celery('product_scraper')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure Celery Beat scheduler
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'


app.conf.beat_schedule = {
    'scrape_amazon_products_every_six_hours': {
        'task': 'scraper.tasks.scrape_amazon_products',
        # 'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        'schedule': crontab(minute='*'),  # Runs every minute
    },
}